"""Check whether the classifier relies on motor speed (RPM) rather than on the fault itself.

F4 (undervoltage) runs at a lower speed than HEALTHY, so RPM features could identify the
operating point instead of the fault. This script:

  1. Prints the RPM distribution per class (median RPM per window).
  2. Re-runs the grouped CV (same folds as train_and_evaluate.py) with:
       a) the deployed 11-feature set
       b) the same set with the 4 RPM features removed
       c) the RPM features only
  3. Reports per-class recall for each variant.

The deployed artifacts are not modified. Results are written to
models/saved_models/speed_confound_check.csv.

Usage (from hardware/esp32-pdm):
    PYTHONPATH=. python3 pdm_enhanced/models/speed_confound_check.py
"""

from __future__ import annotations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score, f1_score, recall_score
from sklearn.model_selection import StratifiedGroupKFold

from pdm_enhanced.models.train_and_evaluate import RF_COMPACT_PARAMS, LABELS

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / "data" / "ml_dataset.csv"
REPORT_PATH = ROOT_DIR / "models" / "saved_models" / "speed_confound_check.csv"

DEPLOYED = [
    "rpm_min", "rpm_median", "rpm_slope_rpm_per_s", "rpm_p2p",
    "acs_dI_dt_slope", "acs_p2p", "az_mean", "ay_rms",
    "ay_p2p", "ax_crest", "az_std",
]
RPM_FEATURES = ["rpm_min", "rpm_median", "rpm_slope_rpm_per_s", "rpm_p2p"]
NON_RPM = [f for f in DEPLOYED if f not in RPM_FEATURES]
SEEDS = [42, 7, 2024]


def per_class_recall(y_true, y_pred) -> dict[str, float]:
    recalls = recall_score(y_true, y_pred, labels=LABELS, average=None, zero_division=0)
    return dict(zip(LABELS, recalls))


def run_variant_seeded(df: pd.DataFrame, features: list[str], seed: int):
    """Out-of-fold predictions with the same grouped folds as train_and_evaluate.py, for one seed."""
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    y_true_all, y_pred_all = [], []
    X, y, groups = df[features], df["fault_id"], df["group"]
    for train_idx, test_idx in cv.split(X, y, groups):
        clf = RandomForestClassifier(**{**RF_COMPACT_PARAMS, "random_state": seed})
        clf.fit(X.iloc[train_idx], y.iloc[train_idx])
        y_pred_all.extend(clf.predict(X.iloc[test_idx]))
        y_true_all.extend(y.iloc[test_idx])
    return np.array(y_true_all), np.array(y_pred_all)


def main() -> None:
    df = pd.read_csv(DATA_PATH)

    print("Median RPM per window, by class (speed separation):")
    speed = df.groupby("fault_id")["rpm_median"].describe(percentiles=[0.1, 0.5, 0.9])
    print(speed[["count", "10%", "50%", "90%"]].round(0).to_string())
    print()

    variants = {
        "deployed (11 features)": DEPLOYED,
        "no RPM features (7)": NON_RPM,
        "RPM features only (4)": RPM_FEATURES,
    }

    rows = []
    for seed in SEEDS:
        for name, feats in variants.items():
            y_true, y_pred = run_variant_seeded(df, feats, seed)
            rec = per_class_recall(y_true, y_pred)
            rows.append({
                "seed": seed,
                "variant": name,
                "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
                "macro_f1": f1_score(y_true, y_pred, labels=LABELS, average="macro", zero_division=0),
                **{f"recall_{k}": v for k, v in rec.items()},
            })

    out = pd.DataFrame(rows)
    summary = out.groupby("variant", sort=False).mean(numeric_only=True).drop(columns="seed")
    summary.round(3).to_csv(REPORT_PATH)

    print("Grouped CV, mean over seeds 42 / 7 / 2024:")
    print(summary.round(3).T.to_string())
    print(f"\nWritten: {REPORT_PATH}")


if __name__ == "__main__":
    main()
