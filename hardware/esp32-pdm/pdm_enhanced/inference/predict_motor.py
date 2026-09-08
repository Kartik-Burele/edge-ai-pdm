"""Production CLI and streaming inference engine for DC motor predictive maintenance.

Features:
- Processes raw ESP32 CSV logs (timestamp_ms, ax, ay, az, acs_adc, rpm)
- Continuous segment checking (never predicts across timestamp logging gaps)
- Rolling sub-second window inference (e.g., 250ms hop size)
- Out-of-Distribution / Anomaly detection gate
- Continuous 0-100% Health Index and operational severity state
- Aggregated file-level consensus classification with confidence breakdown
- Structured JSON telemetry export for IoT / MQTT integration
"""

from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from pdm_enhanced.data_processing.dataset_builder import identify_continuous_segments
from pdm_enhanced.data_processing.feature_extractor import (
    FS,
    WINDOW_SAMPLES,
    extract_window_features,
)
from pdm_enhanced.models.anomaly_detector import MotorAnomalyDetector
from pdm_enhanced.models.health_index import compute_health_index, FAULT_DISPLAY_NAMES

DEFAULT_MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "saved_models" / "pdm_fault_model.pkl"
DEFAULT_ANOMALY_PATH = Path(__file__).resolve().parent.parent / "models" / "saved_models" / "anomaly_detector.pkl"


def predict_stream(
    df_raw: pd.DataFrame,
    model_artifact: dict,
    anomaly_detector: MotorAnomalyDetector | None = None,
    hop_samples: int = 50,
) -> tuple[pd.DataFrame, dict]:
    """Run rolling-window predictive maintenance classification on a raw DataFrame."""
    required_cols = {"timestamp_ms", "ax", "ay", "az", "acs_adc", "rpm"}
    missing = sorted(required_cols - set(df_raw.columns))
    if missing:
        raise ValueError(f"Input CSV is missing required sensor columns: {missing}")

    model = model_artifact["model"]
    features_list = model_artifact["features"]
    labels = model_artifact["labels"]

    segments = identify_continuous_segments(df_raw["timestamp_ms"].to_numpy())
    if not segments:
        raise ValueError("No continuous segments of at least 1.0 second found without timestamp gaps.")

    window_records = []
    window_id = 0
    t_zero = df_raw["timestamp_ms"].iloc[0]

    for seg_idx, (seg_start, seg_end) in enumerate(segments):
        seg_df = df_raw.iloc[seg_start:seg_end].reset_index(drop=True)
        seg_len = len(seg_df)

        curr_idx = 0
        while curr_idx + WINDOW_SAMPLES <= seg_len:
            w_start = curr_idx
            w_end = curr_idx + WINDOW_SAMPLES
            w_df = seg_df.iloc[w_start:w_end]

            t_start_s = (w_df["timestamp_ms"].iloc[0] - t_zero) / 1000.0
            t_end_s = (w_df["timestamp_ms"].iloc[-1] - t_zero) / 1000.0

            feats = extract_window_features(
                ax=w_df["ax"].to_numpy(dtype=float),
                ay=w_df["ay"].to_numpy(dtype=float),
                az=w_df["az"].to_numpy(dtype=float),
                acs_adc=w_df["acs_adc"].to_numpy(dtype=float),
                rpm_raw=w_df["rpm"].to_numpy(dtype=float),
                fs=FS,
            )

            # Check if all required model features are finite
            feat_vector = [feats.get(f, np.nan) for f in features_list]
            if np.all(np.isfinite(feat_vector)):
                X_w = pd.DataFrame([feat_vector], columns=features_list)
                probs = model.predict_proba(X_w)[0]
                pred_label = model.predict(X_w)[0]
                prob_dict = {lbl: float(p) for lbl, p in zip(model.classes_, probs)}

                is_anomaly = False
                if anomaly_detector is not None:
                    is_anomaly = bool(anomaly_detector.predict_anomaly(X_w)[0])

                health_status = compute_health_index(prob_dict, is_anomaly=is_anomaly)

                rec = {
                    "window_id": window_id,
                    "segment": seg_idx,
                    "start_time_s": round(t_start_s, 3),
                    "end_time_s": round(t_end_s, 3),
                    "rpm_mean": round(feats.get("rpm_mean", 0.0), 1),
                    "current_rms": round(feats.get("acs_rms", 0.0), 2),
                    "vib_ay_rms": round(feats.get("ay_rms", 0.0), 4),
                    "prediction": pred_label,
                    "confidence_percent": health_status.confidence_percent,
                    "health_index": health_status.health_index,
                    "health_state": health_status.state,
                    "is_anomaly": is_anomaly,
                }
                for lbl in labels:
                    rec[f"p_{lbl}"] = prob_dict.get(lbl, 0.0)
                window_records.append(rec)
                window_id += 1

            curr_idx += hop_samples

    if not window_records:
        raise ValueError("Could not extract any valid feature windows with valid RPM.")

    results_df = pd.DataFrame(window_records)

    # File-level Aggregation
    pred_counts = Counter(results_df["prediction"])
    top_pred, top_count = pred_counts.most_common(1)[0]
    vote_share = (top_count / len(results_df)) * 100.0

    mean_health_idx = float(results_df["health_index"].mean())
    min_health_idx = float(results_df["health_index"].min())
    anomaly_fraction = float(results_df["is_anomaly"].mean()) * 100.0

    # Probability vector mean
    mean_probs = {lbl: float(results_df[f"p_{lbl}"].mean()) for lbl in labels}
    final_health_status = compute_health_index(
        mean_probs,
        is_anomaly=(anomaly_fraction > 20.0),
    )

    summary = {
        "total_windows_analyzed": len(results_df),
        "continuous_segments": len(segments),
        "consensus_prediction": top_pred,
        "consensus_description": FAULT_DISPLAY_NAMES.get(top_pred, top_pred),
        "vote_share_percent": round(vote_share, 1),
        "mean_confidence_percent": final_health_status.confidence_percent,
        "mean_health_index": round(mean_health_idx, 1),
        "min_health_index": round(min_health_idx, 1),
        "overall_health_state": final_health_status.state,
        "anomaly_window_percent": round(anomaly_fraction, 1),
        "class_probability_distribution": mean_probs,
    }

    return results_df, summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Predictive Maintenance Classifier for DC Motors")
    parser.add_argument("csv", type=Path, help="Path to input raw CSV file")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH, help="Path to trained model artifact")
    parser.add_argument("--anomaly-detector", type=Path, default=DEFAULT_ANOMALY_PATH, help="Path to anomaly detector")
    parser.add_argument("--hop-samples", type=int, default=50, help="Hop size in samples for rolling window (50=250ms)")
    parser.add_argument("--output-csv", type=Path, default=None, help="Path to save per-window predictions")
    parser.add_argument("--json", action="store_true", help="Print output as JSON telemetry payload")
    args = parser.parse_args()

    if not args.csv.is_file():
        parser.error(f"Input CSV not found: {args.csv}")
    if not args.model.is_file():
        parser.error(f"Model artifact not found: {args.model}")

    model_artifact = joblib.load(args.model)
    anomaly_detector = None
    if args.anomaly_detector.is_file():
        anomaly_detector = MotorAnomalyDetector.load(args.anomaly_detector)

    df_raw = pd.read_csv(args.csv)
    results_df, summary = predict_stream(
        df_raw=df_raw,
        model_artifact=model_artifact,
        anomaly_detector=anomaly_detector,
        hop_samples=args.hop_samples,
    )

    if args.output_csv:
        results_df.to_csv(args.output_csv, index=False)

    if args.json:
        print(json.dumps(summary, indent=2))
        return

    # Formatted Terminal Output
    print("\n" + "=" * 65)
    print("        DC MOTOR PREDICTIVE MAINTENANCE DIAGNOSTIC REPORT        ")
    print("=" * 65)
    print(f"Target File         : {args.csv.name}")
    print(f"Windows Analyzed    : {summary['total_windows_analyzed']} (hop: {args.hop_samples/FS*1000:.0f}ms)")
    print(f"Continuous Segments : {summary['continuous_segments']}")
    print("-" * 65)
    print(f"DIAGNOSIS           : {summary['consensus_prediction']} — {summary['consensus_description']}")
    print(f"Model Confidence    : {summary['mean_confidence_percent']:.1f}% (Vote share: {summary['vote_share_percent']:.1f}%)")
    print(f"Health Index        : {summary['mean_health_index']:.1f}% (Min: {summary['min_health_index']:.1f}%)")
    print(f"Operating State     : [{summary['overall_health_state']}]")
    if summary["anomaly_window_percent"] > 0:
        print(f"Anomaly Warning     : {summary['anomaly_window_percent']:.1f}% of windows showed atypical behavior")
    print("-" * 65)
    print("Class Probability Distribution:")
    for lbl, prob in summary["class_probability_distribution"].items():
        bar_len = int(prob * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        print(f"  {lbl:<8} |{bar}| {prob * 100:5.1f}%")
    print("-" * 65)
    print("Recent Windows Sample:")
    sample_view = results_df[["window_id", "start_time_s", "rpm_mean", "current_rms", "prediction", "health_index", "health_state"]].tail(8)
    print(sample_view.to_string(index=False))
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
