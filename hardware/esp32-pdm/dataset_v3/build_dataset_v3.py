"""Create a relabelled master feature table and ML-ready dataset from existing logs.

The source files are never modified.  Fault-file baseline and recovery windows
become HEALTHY; only the inferred intervals in event_label_manifest_v3.csv
retain F1-F4 labels.
"""
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE_MASTER = ROOT.parent / "log_file/output290826/master_features_with_rpm.csv"
MANIFEST = ROOT / "event_label_manifest_v3.csv"
OUTPUT_MASTER = ROOT / "master_features_relabelled_v3.csv"
OUTPUT_ML = ROOT / "ml_dataset_v3.csv"
OUTPUT_SUMMARY = ROOT / "dataset_summary_v3.csv"
OUTPUT_FEATURES = ROOT / "training_features_v3.txt"

META = [
    "dataset_type", "fault_id", "fault_description", "file", "iteration",
    "segment", "window", "start_time_s", "original_fault_id",
    "label_origin", "label_rationale",
]
OPERATING = ["load_A", "load_voltage_V", "psu_current_A", "load_power_W", "supply_voltage_V"]
RPM_DIAGNOSTICS = [
    "rpm_raw_mean", "rpm_raw_median", "rpm_invalid_samples",
    "rpm_valid_fraction", "rpm_invalid_fraction",
]


def main():
    source = pd.read_csv(SOURCE_MASTER)
    manifest = pd.read_csv(MANIFEST)
    required = {"source_file", "window_start", "window_end", "fault_id", "fault_description", "rationale"}
    if missing := required - set(manifest.columns):
        raise ValueError(f"Manifest columns missing: {sorted(missing)}")

    out = source.copy()
    out["original_fault_id"] = out["fault_id"]
    is_original_fault = out["original_fault_id"].ne("HEALTHY")
    out.loc[is_original_fault, "fault_id"] = "HEALTHY"
    out.loc[is_original_fault, "fault_description"] = "Stable baseline or recovery from original fault recording"
    out["label_origin"] = np.where(is_original_fault, "relabelled_healthy", "original_healthy")
    out["label_rationale"] = np.where(is_original_fault, "Outside inferred event interval", "Original healthy recording")

    assigned = pd.Series(False, index=out.index)
    for event in manifest.itertuples(index=False):
        matches = (out["file"] == event.source_file) & out["window"].between(event.window_start, event.window_end)
        if not matches.any():
            raise ValueError(f"No source windows matched manifest row for {event.source_file}")
        if assigned[matches].any():
            raise ValueError(f"Overlapping manifest intervals for {event.source_file}")
        out.loc[matches, "fault_id"] = event.fault_id
        out.loc[matches, "fault_description"] = event.fault_description
        out.loc[matches, "label_origin"] = "inferred_event"
        out.loc[matches, "label_rationale"] = event.rationale
        assigned.loc[matches] = True

    out.to_csv(OUTPUT_MASTER, index=False)

    drop = set(META + OPERATING + RPM_DIAGNOSTICS)
    features = [
        column for column in out.columns
        if column not in drop and pd.api.types.is_numeric_dtype(out[column])
    ]
    finite = np.isfinite(out[features].to_numpy(dtype=float)).all(axis=1)
    ml = out.loc[finite, META + features].copy()
    ml["group"] = ml["file"]
    ml.to_csv(OUTPUT_ML, index=False)
    OUTPUT_FEATURES.write_text("\n".join(features) + "\n")

    summary = pd.DataFrame({
        "windows": ml.groupby("fault_id").size(),
        "recordings": ml.groupby("fault_id")["group"].nunique(),
    }).reset_index()
    summary.to_csv(OUTPUT_SUMMARY, index=False)

    print(f"Source master: {SOURCE_MASTER}")
    print(f"Saved relabelled master: {OUTPUT_MASTER}")
    print(f"Saved ML dataset: {OUTPUT_ML}")
    print(f"Features: {len(features)}")
    print("\nClass summary:")
    print(summary.to_string(index=False))
    print("\nInferred event windows:", int((ml["label_origin"] == "inferred_event").sum()))


if __name__ == "__main__":
    main()
