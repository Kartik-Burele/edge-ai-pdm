"""Classify a new ESP32 motor log with the trained fault model.

The feature calculations deliberately mirror
``make_master_csv_with_RPM_updated.py``.  Do not change one without changing
the other and retraining the model.

Example (run from the PDM_V1 folder):
    python log_file/scripts/predict_motor.py log_file/demo_newcoupler1.csv
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


FS = 200
WINDOW_SAMPLES = FS
RPM_HARD_MIN = 0
RPM_HARD_MAX = 5000
RPM_JUMP_LIMIT = 1000
RPM_MEDIAN_WINDOW = 5
TIMESTAMP_GAP_FACTOR = 3.0

FAULT_NAMES = {
    "HEALTHY": "Healthy",
    "F1": "Repeat load step",
    "F2": "Step load increase",
    "F3": "Load spike",
    "F4": "Undervoltage",
}


def rms(x: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(x, dtype=float) ** 2)))


def peak_to_peak(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    return float(np.max(x) - np.min(x))


def crest_factor(x: np.ndarray) -> float:
    value = rms(x)
    return 0.0 if value == 0 else float(np.max(np.abs(x)) / value)


def spectral_features(x: np.ndarray) -> tuple[float, float, float, float]:
    x = np.asarray(x, dtype=float)
    x = x - np.mean(x)
    magnitude = np.abs(np.fft.rfft(x * np.hanning(len(x))))
    frequencies = np.fft.rfftfreq(len(x), d=1 / FS)
    magnitude[0] = 0
    index = int(np.argmax(magnitude))
    total = np.sum(magnitude)
    centroid = float(np.sum(frequencies * magnitude) / total) if total else 0.0
    return (
        float(frequencies[index]),
        float(magnitude[index]),
        float(np.sum(magnitude ** 2)),
        centroid,
    )


def clean_rpm(rpm: np.ndarray) -> np.ndarray:
    """Apply the same RPM validation used when the model was trained."""
    raw = np.asarray(rpm, dtype=float)
    valid = np.isfinite(raw) & (raw > RPM_HARD_MIN) & (raw <= RPM_HARD_MAX)
    median = pd.Series(raw).rolling(
        window=RPM_MEDIAN_WINDOW, center=True, min_periods=1
    ).median().to_numpy()
    valid &= ~np.isfinite(median) | (np.abs(raw - median) <= RPM_JUMP_LIMIT)

    if len(raw) > 1:
        jump_invalid = np.zeros(len(raw), dtype=bool)
        jumps = np.abs(np.diff(raw)) > RPM_JUMP_LIMIT
        jump_invalid[1:] |= jumps
        jump_invalid[:-1] |= jumps
        valid &= ~jump_invalid

    cleaned = raw.copy()
    cleaned[~valid] = np.nan
    return cleaned


def rpm_features(cleaned: np.ndarray) -> dict[str, float]:
    valid = cleaned[np.isfinite(cleaned)]
    if not len(valid):
        return {key: np.nan for key in (
            "rpm_mean", "rpm_median", "rpm_std", "rpm_min", "rpm_max",
            "rpm_p2p", "rpm_cv_percent", "rpm_slope_rpm_per_s",
        )}

    indices = np.where(np.isfinite(cleaned))[0]
    slope = np.polyfit(indices / FS, cleaned[indices], 1)[0] if len(indices) >= 2 else np.nan
    mean = float(np.mean(valid))
    std = float(np.std(valid))
    return {
        "rpm_mean": mean,
        "rpm_median": float(np.median(valid)),
        "rpm_std": std,
        "rpm_min": float(np.min(valid)),
        "rpm_max": float(np.max(valid)),
        "rpm_p2p": float(np.max(valid) - np.min(valid)),
        "rpm_cv_percent": std / mean * 100 if mean > 0 else np.nan,
        "rpm_slope_rpm_per_s": float(slope),
    }


def continuous_segments(timestamps: np.ndarray) -> tuple[list[tuple[int, int]], int]:
    """Return sample ranges that do not cross a timestamp logging gap."""
    if len(timestamps) < 2:
        return [], 0
    intervals = np.diff(np.asarray(timestamps, dtype=float))
    positive = intervals[intervals > 0]
    if not len(positive):
        return [], 0
    gaps = np.where(intervals > TIMESTAMP_GAP_FACTOR * np.median(positive))[0]
    boundaries = [0, *(gaps + 1), len(timestamps)]
    return [
        (start, end) for start, end in zip(boundaries, boundaries[1:])
        if end - start >= WINDOW_SAMPLES
    ], len(gaps)


def window_features(window: pd.DataFrame, cleaned_rpm: np.ndarray) -> dict[str, float]:
    ax = window["ax"].to_numpy(dtype=float)
    ay = window["ay"].to_numpy(dtype=float)
    az = window["az"].to_numpy(dtype=float)
    acs = window["acs_adc"].to_numpy(dtype=float)
    ax_dynamic, ay_dynamic, az_dynamic = ax - ax.mean(), ay - ay.mean(), az - az.mean()
    magnitude = np.sqrt(ax_dynamic**2 + ay_dynamic**2 + az_dynamic**2)
    dominant_frequency, dominant_amplitude, spectral_energy, spectral_centroid = spectral_features(magnitude)

    result = {
        "ax_mean": float(np.mean(ax)), "ax_std": float(np.std(ax_dynamic)),
        "ax_rms": rms(ax_dynamic), "ax_peak": float(np.max(np.abs(ax_dynamic))),
        "ax_p2p": peak_to_peak(ax_dynamic), "ax_crest": crest_factor(ax_dynamic),
        "ay_mean": float(np.mean(ay)), "ay_std": float(np.std(ay_dynamic)),
        "ay_rms": rms(ay_dynamic), "ay_peak": float(np.max(np.abs(ay_dynamic))),
        "ay_p2p": peak_to_peak(ay_dynamic), "ay_crest": crest_factor(ay_dynamic),
        "az_mean": float(np.mean(az)), "az_std": float(np.std(az_dynamic)),
        "az_rms": rms(az_dynamic), "az_peak": float(np.max(np.abs(az_dynamic))),
        "az_p2p": peak_to_peak(az_dynamic), "az_crest": crest_factor(az_dynamic),
        "acc_mag_rms": rms(magnitude), "acc_mag_std": float(np.std(magnitude)),
        "acc_mag_peak": float(np.max(np.abs(magnitude)),), "acc_mag_p2p": peak_to_peak(magnitude),
        "acs_mean": float(np.mean(acs)), "acs_std": float(np.std(acs)),
        "acs_rms": rms(acs), "acs_min": float(np.min(acs)),
        "acs_max": float(np.max(acs)), "acs_p2p": peak_to_peak(acs),
        "dominant_frequency_Hz": dominant_frequency,
        "dominant_amplitude": dominant_amplitude,
        "spectral_energy": spectral_energy,
        "spectral_centroid_Hz": spectral_centroid,
    }
    result.update(rpm_features(cleaned_rpm))
    return result


def build_feature_table(log: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    required = {"timestamp_ms", "ax", "ay", "az", "acs_adc", "rpm"}
    missing = sorted(required - set(log.columns))
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")

    segments, gap_count = continuous_segments(log["timestamp_ms"].to_numpy())
    cleaned = clean_rpm(log["rpm"].to_numpy(dtype=float))
    rows = []
    number = 0
    for segment_id, (start, end) in enumerate(segments):
        for window_start in range(start, start + ((end - start) // WINDOW_SAMPLES) * WINDOW_SAMPLES, WINDOW_SAMPLES):
            window_end = window_start + WINDOW_SAMPLES
            row = window_features(log.iloc[window_start:window_end], cleaned[window_start:window_end])
            row.update({
                "window": number,
                "segment": segment_id,
                "start_time_s": (log["timestamp_ms"].iloc[window_start] - log["timestamp_ms"].iloc[0]) / 1000,
            })
            rows.append(row)
            number += 1
    return pd.DataFrame(rows), gap_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Predict ESP32 motor condition from a CSV log.")
    parser.add_argument("csv", type=Path, help="ESP32 CSV with timestamp_ms, ax, ay, az, acs_adc, rpm")
    parser.add_argument("--model", type=Path, default=Path("log_file/output290826/motor_fault_model.pkl"))
    parser.add_argument("--output", type=Path, help="Where to save per-window predictions (CSV)")
    args = parser.parse_args()

    if not args.csv.is_file():
        parser.error(f"CSV not found: {args.csv}")
    if not args.model.is_file():
        parser.error(f"Model not found: {args.model}")

    artifact = joblib.load(args.model)
    if not {"model", "features", "labels"} <= artifact.keys():
        raise ValueError("Model file is not a compatible motor_fault_model.pkl artifact.")

    feature_table, gap_count = build_feature_table(pd.read_csv(args.csv))
    if feature_table.empty:
        raise ValueError("No complete 1-second windows found after excluding timestamp gaps.")
    features = artifact["features"]
    missing = sorted(set(features) - set(feature_table.columns))
    if missing:
        raise ValueError(f"Feature mismatch; prediction cannot continue: {missing}")
    X = feature_table[features]
    # Training removed windows with incomplete cleaned-RPM features.  Apply
    # the identical policy here rather than allowing one bad trailing window
    # (for example, an encoder stopped at the end of logging) to abort a demo.
    valid_windows = np.isfinite(X.to_numpy(dtype=float)).all(axis=1)
    skipped_windows = int((~valid_windows).sum())
    feature_table = feature_table.loc[valid_windows].copy()
    X = feature_table[features]
    if feature_table.empty:
        raise ValueError("Every complete window has invalid feature values; check the RPM signal.")

    model = artifact["model"]
    predictions = model.predict(X)
    probabilities = model.predict_proba(X)
    feature_table["prediction"] = predictions
    feature_table["confidence_percent"] = np.max(probabilities, axis=1) * 100

    counts = Counter(predictions)
    max_count = max(counts.values())
    tied = {label for label, count in counts.items() if count == max_count}
    mean_probabilities = probabilities.mean(axis=0)
    final_label = max(tied, key=lambda label: mean_probabilities[list(model.classes_).index(label)])
    final_confidence = mean_probabilities[list(model.classes_).index(final_label)] * 100

    output = args.output or args.csv.with_name(f"{args.csv.stem}_predictions.csv")
    feature_table.to_csv(output, index=False)

    print("=" * 48)
    print("MOTOR PREDICTION")
    print("=" * 48)
    print(f"Input CSV         : {args.csv}")
    print(f"Windows analyzed  : {len(feature_table)}")
    if skipped_windows:
        print(f"Windows skipped   : {skipped_windows} (incomplete/invalid features)")
    print(f"Timestamp gaps    : {gap_count} (windows never cross a gap)")
    print("\nPer-window predictions:")
    for row in feature_table.itertuples(index=False):
        print(f"  {row.window:02d}  t={row.start_time_s:6.2f}s  {row.prediction:<7}  {row.confidence_percent:5.1f}%")
    print("\nFinal prediction:")
    print(f"  {final_label} — {FAULT_NAMES.get(final_label, final_label)}")
    print(f"  Vote share: {max_count}/{len(feature_table)} ({max_count / len(feature_table) * 100:.1f}%)")
    print(f"  Mean model confidence for final class: {final_confidence:.1f}%")
    print(f"\nPer-window results saved to: {output}")


if __name__ == "__main__":
    main()
