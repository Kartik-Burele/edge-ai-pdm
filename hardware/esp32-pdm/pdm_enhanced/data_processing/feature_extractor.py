"""Comprehensive feature extraction engine for predictive maintenance of DC motors.

Includes:
- Time-domain dynamic vibration statistics (Ax, Ay, Az, Acc Magnitude)
- Rotational order-tracked harmonic energy (1X, 2X, 3X shaft speed multiples)
- Physical DC electromechanical features (RPM/Current ratio, dI/dt, dRPM/dt)
- ACS712 current statistics (RMS, peak-to-peak, min, max, std, mean)
- Robust RPM outlier rejection and validation
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats

FS = 200  # Sampling frequency in Hz
WINDOW_SAMPLES = FS  # 1 second default window

# RPM validation thresholds
RPM_HARD_MIN = 0.0
RPM_HARD_MAX = 5000.0
RPM_JUMP_LIMIT = 1000.0
RPM_MEDIAN_WINDOW = 5
TIMESTAMP_GAP_FACTOR = 3.0


def clean_rpm(raw_rpm: np.ndarray) -> np.ndarray:
    """Filter raw RPM using hard bounds, running median filter, and point-to-point jump limits.
    
    Invalid samples are replaced with np.nan while preserving raw array length.
    """
    raw = np.asarray(raw_rpm, dtype=float)
    bounded = np.isfinite(raw) & (raw > RPM_HARD_MIN) & (raw <= RPM_HARD_MAX)
    valid = bounded.copy()

    if len(raw) >= RPM_MEDIAN_WINDOW:
        median = pd.Series(np.where(bounded, raw, np.nan)).rolling(
            window=RPM_MEDIAN_WINDOW, center=True, min_periods=1
        ).median().to_numpy()
        valid &= ~np.isfinite(median) | (np.abs(raw - median) <= RPM_JUMP_LIMIT)

    if len(raw) > 1:
        raw_b = np.where(bounded, raw, np.nan)
        diffs = np.abs(np.diff(raw_b))
        jumps = np.isfinite(diffs) & (diffs > RPM_JUMP_LIMIT)
        jump_invalid = np.zeros(len(raw), dtype=bool)
        jump_invalid[1:] |= jumps
        jump_invalid[:-1] |= jumps
        valid &= ~jump_invalid

    cleaned = raw.copy()
    cleaned[~valid] = np.nan
    return cleaned


def rms(x: np.ndarray) -> float:
    """Root Mean Square."""
    x = np.asarray(x, dtype=float)
    return float(np.sqrt(np.mean(x ** 2))) if len(x) else 0.0


def peak_to_peak(x: np.ndarray) -> float:
    """Peak-to-peak amplitude."""
    x = np.asarray(x, dtype=float)
    return float(np.ptp(x)) if len(x) else 0.0


def crest_factor(x: np.ndarray) -> float:
    """Crest factor: peak amplitude divided by RMS value."""
    x = np.asarray(x, dtype=float)
    r = rms(x)
    return float(np.max(np.abs(x)) / r) if r > 1e-9 else 0.0


def signal_skewness(x: np.ndarray) -> float:
    """Statistical skewness."""
    x = np.asarray(x, dtype=float)
    if len(x) < 3 or np.std(x) < 1e-9:
        return 0.0
    return float(stats.skew(x, bias=False))


def signal_kurtosis(x: np.ndarray) -> float:
    """Statistical excess kurtosis."""
    x = np.asarray(x, dtype=float)
    if len(x) < 4 or np.std(x) < 1e-9:
        return 0.0
    return float(stats.kurtosis(x, bias=False))


def spectral_and_order_features(dynamic_signal: np.ndarray, rpm_mean: float, fs: int = FS) -> dict[str, float]:
    """Compute FFT spectral energy, centroid, dominant peak, and RPM-synchronized order harmonics (1X, 2X, 3X)."""
    n = len(dynamic_signal)
    if n < 10:
        return {
            "dominant_frequency_Hz": 0.0,
            "dominant_amplitude": 0.0,
            "spectral_energy": 0.0,
            "spectral_centroid_Hz": 0.0,
            "order_1x_energy": 0.0,
            "order_2x_energy": 0.0,
            "order_3x_energy": 0.0,
        }

    window = np.hanning(n)
    fft_vals = np.fft.rfft(dynamic_signal * window)
    magnitude = np.abs(fft_vals)
    freqs = np.fft.rfftfreq(n, d=1.0 / fs)
    magnitude[0] = 0.0  # Zero DC component

    total_mag = float(np.sum(magnitude))
    centroid = float(np.sum(freqs * magnitude) / total_mag) if total_mag > 1e-9 else 0.0
    dom_idx = int(np.argmax(magnitude))
    dom_freq = float(freqs[dom_idx])
    dom_amp = float(magnitude[dom_idx])
    spectral_energy = float(np.sum(magnitude ** 2))

    # Order tracking: 1X = shaft rotation frequency (Hz)
    f_shaft = (rpm_mean / 60.0) if (np.isfinite(rpm_mean) and rpm_mean > 0) else 0.0
    
    def extract_harmonic_band_energy(target_f: float, bandwidth_hz: float = 2.5) -> float:
        if target_f <= 0 or target_f >= fs / 2:
            return 0.0
        mask = (freqs >= target_f - bandwidth_hz) & (freqs <= target_f + bandwidth_hz)
        return float(np.sum(magnitude[mask] ** 2)) if np.any(mask) else 0.0

    order_1x = extract_harmonic_band_energy(f_shaft * 1.0)
    order_2x = extract_harmonic_band_energy(f_shaft * 2.0)
    order_3x = extract_harmonic_band_energy(f_shaft * 3.0)

    return {
        "dominant_frequency_Hz": dom_freq,
        "dominant_amplitude": dom_amp,
        "spectral_energy": spectral_energy,
        "spectral_centroid_Hz": centroid,
        "order_1x_energy": order_1x,
        "order_2x_energy": order_2x,
        "order_3x_energy": order_3x,
    }


def compute_rpm_features(cleaned_rpm: np.ndarray, fs: int = FS) -> dict[str, float]:
    """Compute statistical and dynamic trajectory features from cleaned RPM."""
    valid = cleaned_rpm[np.isfinite(cleaned_rpm)]
    total_samples = len(cleaned_rpm)
    valid_count = len(valid)

    diagnostics = {
        "rpm_valid_fraction": valid_count / total_samples if total_samples > 0 else 0.0,
        "rpm_invalid_samples": total_samples - valid_count,
    }

    if valid_count < 2:
        feats = {
            "rpm_mean": np.nan, "rpm_median": np.nan, "rpm_std": np.nan,
            "rpm_min": np.nan, "rpm_max": np.nan, "rpm_p2p": np.nan,
            "rpm_cv_percent": np.nan, "rpm_slope_rpm_per_s": np.nan,
        }
        feats.update(diagnostics)
        return feats

    mean_val = float(np.mean(valid))
    std_val = float(np.std(valid, ddof=0))
    valid_indices = np.where(np.isfinite(cleaned_rpm))[0]

    slope = float(np.polyfit(valid_indices / fs, valid, 1)[0]) if len(valid_indices) >= 2 else 0.0

    feats = {
        "rpm_mean": mean_val,
        "rpm_median": float(np.median(valid)),
        "rpm_std": std_val,
        "rpm_min": float(np.min(valid)),
        "rpm_max": float(np.max(valid)),
        "rpm_p2p": float(np.max(valid) - np.min(valid)),
        "rpm_cv_percent": (std_val / mean_val * 100.0) if mean_val > 1e-6 else 0.0,
        "rpm_slope_rpm_per_s": slope,
    }
    feats.update(diagnostics)
    return feats


def compute_current_and_coupling_features(acs_adc: np.ndarray, rpm_mean: float, fs: int = FS) -> dict[str, float]:
    """Compute electrical ACS712 features, derivative rates, and electromechanical coupling ratios."""
    acs = np.asarray(acs_adc, dtype=float)
    mean_i = float(np.mean(acs))
    rms_i = rms(acs)
    std_i = float(np.std(acs, ddof=0))
    p2p_i = peak_to_peak(acs)
    min_i = float(np.min(acs))
    max_i = float(np.max(acs))

    # Current rate of change (dI/dt)
    if len(acs) >= 2:
        t = np.arange(len(acs)) / fs
        dI_dt_slope = float(np.polyfit(t, acs, 1)[0])
        dI_dt_max = float(np.max(np.abs(np.diff(acs))) * fs)
    else:
        dI_dt_slope = 0.0
        dI_dt_max = 0.0

    # Electromechanical proxy ratio: RPM / (ACS_RMS + epsilon)
    # A sudden drop in ratio indicates electrical overload / step increase / undervoltage.
    rpm_to_current_ratio = (rpm_mean / (rms_i + 1e-3)) if (np.isfinite(rpm_mean) and rpm_mean > 0) else 0.0

    return {
        "acs_mean": mean_i,
        "acs_std": std_i,
        "acs_rms": rms_i,
        "acs_min": min_i,
        "acs_max": max_i,
        "acs_p2p": p2p_i,
        "acs_dI_dt_slope": dI_dt_slope,
        "acs_dI_dt_max": dI_dt_max,
        "rpm_to_current_ratio": rpm_to_current_ratio,
    }


def extract_window_features(
    ax: np.ndarray,
    ay: np.ndarray,
    az: np.ndarray,
    acs_adc: np.ndarray,
    rpm_raw: np.ndarray,
    fs: int = FS,
) -> dict[str, float]:
    """Extract full feature dictionary from a single time window."""
    # Dynamic (mean-subtracted) vibration signals
    ax_dyn = ax - np.mean(ax)
    ay_dyn = ay - np.mean(ay)
    az_dyn = az - np.mean(az)
    acc_mag_dyn = np.sqrt(ax_dyn ** 2 + ay_dyn ** 2 + az_dyn ** 2)

    # RPM extraction
    cleaned_rpm = clean_rpm(rpm_raw)
    rpm_feats = compute_rpm_features(cleaned_rpm, fs=fs)
    rpm_mean_val = rpm_feats.get("rpm_mean", 0.0)

    # Spectral & Order Tracking
    spec_feats = spectral_and_order_features(acc_mag_dyn, rpm_mean=rpm_mean_val, fs=fs)

    # Current & Electromechanical Features
    elec_feats = compute_current_and_coupling_features(acs_adc, rpm_mean=rpm_mean_val, fs=fs)

    # Vibration Statistics
    vib_feats = {
        "ax_mean": float(np.mean(ax)), "ax_std": float(np.std(ax_dyn, ddof=0)),
        "ax_rms": rms(ax_dyn), "ax_peak": float(np.max(np.abs(ax_dyn))),
        "ax_p2p": peak_to_peak(ax_dyn), "ax_crest": crest_factor(ax_dyn),
        "ax_skew": signal_skewness(ax_dyn), "ax_kurt": signal_kurtosis(ax_dyn),

        "ay_mean": float(np.mean(ay)), "ay_std": float(np.std(ay_dyn, ddof=0)),
        "ay_rms": rms(ay_dyn), "ay_peak": float(np.max(np.abs(ay_dyn))),
        "ay_p2p": peak_to_peak(ay_dyn), "ay_crest": crest_factor(ay_dyn),
        "ay_skew": signal_skewness(ay_dyn), "ay_kurt": signal_kurtosis(ay_dyn),

        "az_mean": float(np.mean(az)), "az_std": float(np.std(az_dyn, ddof=0)),
        "az_rms": rms(az_dyn), "az_peak": float(np.max(np.abs(az_dyn))),
        "az_p2p": peak_to_peak(az_dyn), "az_crest": crest_factor(az_dyn),
        "az_skew": signal_skewness(az_dyn), "az_kurt": signal_kurtosis(az_dyn),

        "acc_mag_rms": rms(acc_mag_dyn), "acc_mag_std": float(np.std(acc_mag_dyn, ddof=0)),
        "acc_mag_peak": float(np.max(acc_mag_dyn)), "acc_mag_p2p": peak_to_peak(acc_mag_dyn),
        "acc_mag_crest": crest_factor(acc_mag_dyn),
    }

    full_features = {}
    full_features.update(vib_feats)
    full_features.update(spec_feats)
    full_features.update(elec_feats)
    full_features.update(rpm_feats)
    return full_features
