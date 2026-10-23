"""Compare embeddable classifiers on the compact 12-feature set using the same grouped CV.

Runs several candidate models with StratifiedGroupKFold (grouped by recording file),
repeated over a few seeds because the dataset has only 45 recordings. Reports balanced
accuracy and macro F1, plus a rough size of each model for embedded deployment.

Usage (from hardware/esp32-pdm):
    PYTHONPATH=. python3 pdm_enhanced/models/compare_models.py
"""

from __future__ import annotations
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, f1_score
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / "data" / "ml_dataset.csv"
REPORT_PATH = ROOT_DIR / "models" / "saved_models" / "model_comparison.csv"

LABELS = ["HEALTHY", "F1", "F2", "F3", "F4"]
COMPACT_FEATURES = [
    "rpm_min", "rpm_median", "rpm_slope_rpm_per_s", "rpm_p2p",
    "acs_dI_dt_slope", "acs_p2p", "az_mean", "ay_rms",
    "ay_p2p", "ax_crest", "order_2x_energy", "az_std",
]
SEEDS = [42, 7, 2024]


def candidate_models(seed: int) -> dict:
    """Candidate models. Sizes are chosen to be embeddable on the ESP32-S3."""
    return {
        "RF_35x6 (current)": RandomForestClassifier(
            n_estimators=35, max_depth=6, min_samples_leaf=2, max_features="sqrt",
            class_weight="balanced_subsample", random_state=seed, n_jobs=-1),
        "ExtraTrees_35x6": ExtraTreesClassifier(
            n_estimators=35, max_depth=6, min_samples_leaf=2,
            class_weight="balanced_subsample", random_state=seed, n_jobs=-1),
        "DecisionTree_d6": DecisionTreeClassifier(
            max_depth=6, min_samples_leaf=2, class_weight="balanced", random_state=seed),
        "LogReg_standardized": make_pipeline(
            StandardScaler(),
            LogisticRegression(C=1.0, max_iter=5000, class_weight="balanced")),
        "GaussianNB": GaussianNB(),
        "GradBoost_30x3": GradientBoostingClassifier(
            n_estimators=30, max_depth=3, learning_rate=0.1, random_state=seed),
    }


def model_size_hint(model) -> str:
    """Rough size indicator for the embedded budget."""
    if hasattr(model, "estimators_"):
        nodes = sum(est.tree_.node_count for est in np.ravel(model.estimators_))
        return f"{nodes} tree nodes"
    if hasattr(model, "tree_"):
        return f"{model.tree_.node_count} tree nodes"
    if hasattr(model, "coef_"):
        return f"{model.coef_.size + model.intercept_.size} weights"
    if hasattr(model, "theta_"):
        return f"{model.theta_.size * 2 + model.class_prior_.size} parameters"
    return "n/a"


def run_cv(X: pd.DataFrame, y: pd.Series, groups: pd.Series, seed: int) -> dict:
    """Return metrics per model for one CV seed."""
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    results: dict[str, dict] = {}
    for train_idx, test_idx in cv.split(X, y, groups):
        X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
        X_te, y_te = X.iloc[test_idx], y.iloc[test_idx]
        for name, model in candidate_models(seed).items():
            fit_kwargs = {}
            if name.startswith("GradBoost"):
                # GradientBoosting has no class_weight, so weight samples explicitly
                counts = y_tr.value_counts()
                fit_kwargs["sample_weight"] = y_tr.map(len(y_tr) / (len(counts) * counts)).to_numpy()
            model.fit(X_tr, y_tr, **fit_kwargs)
            pred = model.predict(X_te)
            r = results.setdefault(name, {"true": [], "pred": [], "size": model_size_hint(model)})
            r["true"].extend(y_te)
            r["pred"].extend(pred)
    return results


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    X, y, groups = df[COMPACT_FEATURES], df["fault_id"], df["group"]

    rows = []
    for seed in SEEDS:
        res = run_cv(X, y, groups, seed)
        for name, r in res.items():
            rows.append({
                "seed": seed,
                "model": name,
                "balanced_accuracy": balanced_accuracy_score(r["true"], r["pred"]),
                "macro_f1": f1_score(r["true"], r["pred"], labels=LABELS, average="macro", zero_division=0),
                "size": r["size"],
            })

    out = pd.DataFrame(rows)
    summary = (
        out.groupby("model")
        .agg(balanced_accuracy_mean=("balanced_accuracy", "mean"),
             balanced_accuracy_std=("balanced_accuracy", "std"),
             macro_f1_mean=("macro_f1", "mean"),
             macro_f1_std=("macro_f1", "std"),
             size=("size", "first"))
        .sort_values("macro_f1_mean", ascending=False)
        .reset_index()
    )
    out.to_csv(REPORT_PATH.with_name("model_comparison_per_seed.csv"), index=False)
    summary.to_csv(REPORT_PATH, index=False)
    print(f"Seeds: {SEEDS}  |  Features: {len(COMPACT_FEATURES)} (compact set)  |  Windows: {len(df)}")
    print(summary.round(3).to_string(index=False))
    print(f"\nWritten: {REPORT_PATH}")


if __name__ == "__main__":
    main()
