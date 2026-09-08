"""Build an enhanced, transient-aware dataset for DC motor predictive maintenance.

Features:
- Continuous segment identification across timestamp gaps
- Adaptive sliding windowing (75% overlap / 0.25s hop during transient event intervals, 1.0s hop during baseline/healthy)
- Order tracking and physical electromechanical features
- Output validation with group tags for leakage-free cross-validation
"""

from __future__ import annotations
import glob
import os
import re
from pathlib import Path

import numpy as np
import pandas as pd

from pdm_enhanced.data_processing.feature_extractor import (
    FS,
    WINDOW_SAMPLES,
    TIMESTAMP_GAP_FACTOR,
    extract_window_features,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = ROOT_DIR.parent
RAW_DIR = WORKSPACE_ROOT / "log_file" / "29_08_26"
DATA_DIR = ROOT_DIR / "data"
MANIFEST_PATH = DATA_DIR / "event_manifest.csv"

MASTER_CSV = DATA_DIR / "master_features.csv"
ML_DATASET_CSV = DATA_DIR / "ml_dataset.csv"
SUMMARY_CSV = DATA_DIR / "dataset_summary.csv"
FEATURE_LIST_TXT = DATA_DIR / "feature_list.txt"

TRANSIENT_HOP_SAMPLES = 50  # 0.25s hop (75% overlap) for transient fault intervals
STEADY_HOP_SAMPLES = 200    # 1.0s hop (0% overlap) for steady-state healthy intervals

META_COLUMNS = [
    "file", "group", "dataset_type", "fault_id", "fault_description",
    "iteration", "segment", "window_id", "start_time_s", "end_time_s",
    "is_transient_event", "label_origin", "label_rationale",
]

RPM_DIAGNOSTICS = [
    "rpm_valid_fraction", "rpm_invalid_samples",
]


def identify_continuous_segments(timestamps_ms: np.ndarray) -> list[tuple[int, int]]:
    """Identify sample index boundaries that do not cross timestamp discontinuities."""
    if len(timestamps_ms) < 2:
        return []
    intervals = np.diff(timestamps_ms.astype(float))
    positive = intervals[intervals > 0]
    if len(positive) == 0:
        return []
    median_dt = np.median(positive)
    gap_threshold = TIMESTAMP_GAP_FACTOR * median_dt
    gap_indices = np.where(intervals > gap_threshold)[0]
    boundaries = [0, *(gap_indices + 1), len(timestamps_ms)]
    return [
        (start, end)
        for start, end in zip(boundaries, boundaries[1:])
        if end - start >= WINDOW_SAMPLES
    ]


def parse_filename_metadata(filename: str) -> dict:
    """Parse fault type, iteration, and dataset type from raw CSV filename."""
    base = os.path.basename(filename)
    iter_match = re.search(r'_(\d+)\.csv$', base)
    iteration = int(iter_match.group(1)) if iter_match else 1

    if base.startswith("healthy_"):
        return {
            "dataset_type": "healthy",
            "base_fault_id": "HEALTHY",
            "base_description": "Healthy steady-state baseline",
            "iteration": iteration,
        }
    elif base.startswith("F1_"):
        return {
            "dataset_type": "fault",
            "base_fault_id": "F1",
            "base_description": "Repeat load step (0.4A - 0.8A)",
            "iteration": iteration,
        }
    elif base.startswith("F2_"):
        return {
            "dataset_type": "fault",
            "base_fault_id": "F2",
            "base_description": "Step load increase (0.3A - 1.0A)",
            "iteration": iteration,
        }
    elif base.startswith("F3_"):
        return {
            "dataset_type": "fault",
            "base_fault_id": "F3",
            "base_description": "Load current spike (0.2A - 1.0A)",
            "iteration": iteration,
        }
    elif base.startswith("F4_"):
        return {
            "dataset_type": "fault",
            "base_fault_id": "F4",
            "base_description": "Undervoltage (9V - 12V @ 1A)",
            "iteration": iteration,
        }
    return {
        "dataset_type": "unknown",
        "base_fault_id": "UNKNOWN",
        "base_description": "Unknown condition",
        "iteration": iteration,
    }


def build_dataset() -> pd.DataFrame:
    """Read all raw CSVs, apply event-aware adaptive windowing, and extract features."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest = pd.read_csv(MANIFEST_PATH) if MANIFEST_PATH.exists() else pd.DataFrame()
    raw_files = sorted(glob.glob(str(RAW_DIR / "*.csv")))
    if not raw_files:
        raise FileNotFoundError(f"No CSV files found in {RAW_DIR}")

    all_rows = []
    print(f"Processing {len(raw_files)} raw CSV files from {RAW_DIR}...")

    for file_path in raw_files:
        file_name = os.path.basename(file_path)
        df_raw = pd.read_csv(file_path)
        meta = parse_filename_metadata(file_name)

        # File-specific event intervals from manifest
        file_manifest = manifest[manifest["source_file"] == file_name] if not manifest.empty else pd.DataFrame()

        # Find continuous recording segments (avoiding gaps)
        segments = identify_continuous_segments(df_raw["timestamp_ms"].to_numpy())
        if not segments:
            continue

        window_counter = 0
        for seg_idx, (seg_start, seg_end) in enumerate(segments):
            seg_df = df_raw.iloc[seg_start:seg_end].reset_index(drop=True)
            seg_len = len(seg_df)
            t_base = seg_df["timestamp_ms"].iloc[0]

            # Generate windows using adaptive stepping
            curr_idx = 0
            while curr_idx + WINDOW_SAMPLES <= seg_len:
                w_start = curr_idx
                w_end = curr_idx + WINDOW_SAMPLES
                window_df = seg_df.iloc[w_start:w_end]

                t_start_s = (window_df["timestamp_ms"].iloc[0] - t_base) / 1000.0
                t_end_s = (window_df["timestamp_ms"].iloc[-1] - t_base) / 1000.0
                center_sec = (t_start_s + t_end_s) / 2.0

                # Determine whether this window falls in a transient event interval
                is_event = False
                event_row = None
                if not file_manifest.empty:
                    for e in file_manifest.itertuples():
                        # Window ranges in manifest are in seconds (~ 1s increments)
                        if e.window_start <= center_sec <= (e.window_end + 1.0):
                            is_event = True
                            event_row = e
                            break

                if meta["dataset_type"] == "healthy":
                    fault_id = "HEALTHY"
                    fault_desc = "Healthy steady-state baseline"
                    label_origin = "healthy_run"
                    rationale = "Controlled healthy operating point"
                    hop = STEADY_HOP_SAMPLES
                elif is_event and event_row is not None:
                    fault_id = event_row.fault_id
                    fault_desc = event_row.fault_description
                    label_origin = "inferred_event"
                    rationale = event_row.rationale
                    hop = TRANSIENT_HOP_SAMPLES  # 75% overlap on active transient intervals
                else:
                    fault_id = "HEALTHY"
                    fault_desc = "Baseline/recovery region of fault run"
                    label_origin = "relabelled_healthy"
                    rationale = "Outside transient fault interval"
                    hop = STEADY_HOP_SAMPLES

                # Extract features
                features = extract_window_features(
                    ax=window_df["ax"].to_numpy(dtype=float),
                    ay=window_df["ay"].to_numpy(dtype=float),
                    az=window_df["az"].to_numpy(dtype=float),
                    acs_adc=window_df["acs_adc"].to_numpy(dtype=float),
                    rpm_raw=window_df["rpm"].to_numpy(dtype=float),
                    fs=FS,
                )

                row = {
                    "file": file_name,
                    "group": file_name,
                    "dataset_type": meta["dataset_type"],
                    "fault_id": fault_id,
                    "fault_description": fault_desc,
                    "iteration": meta["iteration"],
                    "segment": seg_idx,
                    "window_id": window_counter,
                    "start_time_s": t_start_s,
                    "end_time_s": t_end_s,
                    "is_transient_event": is_event,
                    "label_origin": label_origin,
                    "label_rationale": rationale,
                }
                row.update(features)
                all_rows.append(row)
                window_counter += 1
                curr_idx += hop

    master_df = pd.DataFrame(all_rows)
    master_df.to_csv(MASTER_CSV, index=False)
    print(f"Master features saved: {MASTER_CSV} (Total windows: {len(master_df)})")

    # Select numerical feature columns for ML
    exclude = set(META_COLUMNS + RPM_DIAGNOSTICS)
    feature_cols = [
        c for c in master_df.columns
        if c not in exclude and pd.api.types.is_numeric_dtype(master_df[c])
    ]

    # Filter rows with finite features (drop windows where RPM was entirely invalid)
    finite_mask = np.isfinite(master_df[feature_cols].to_numpy(dtype=float)).all(axis=1)
    ml_df = master_df.loc[finite_mask, META_COLUMNS + feature_cols].copy()
    ml_df.to_csv(ML_DATASET_CSV, index=False)

    FEATURE_LIST_TXT.write_text("\n".join(feature_cols) + "\n")

    # Summary
    summary = ml_df.groupby("fault_id").agg(
        windows=("window_id", "count"),
        independent_files=("group", "nunique"),
        transient_windows=("is_transient_event", "sum"),
    ).reset_index()
    summary.to_csv(SUMMARY_CSV, index=False)

    print(f"\nML Dataset saved: {ML_DATASET_CSV}")
    print(f"Total ML windows: {len(ml_df)} across {ml_df['group'].nunique()} independent files")
    print(f"Features: {len(feature_cols)}")
    print("\nDataset Summary by Class:")
    print(summary.to_string(index=False))

    return ml_df


if __name__ == "__main__":
    build_dataset()
