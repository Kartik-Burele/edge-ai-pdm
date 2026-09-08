"""Train a 40-feature reference Random Forest from ml_dataset_v3.csv."""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report
from sklearn.model_selection import StratifiedGroupKFold


ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "ml_dataset_v3.csv"
MODEL_OUTPUT = ROOT / "motor_fault_model_v3.pkl"
REPORT_OUTPUT = ROOT / "training_report_v3.txt"
META = [
    "dataset_type", "fault_id", "fault_description", "file", "iteration",
    "segment", "window", "start_time_s", "original_fault_id", "label_origin",
    "label_rationale", "group",
]


def main():
    df = pd.read_csv(DATASET)
    features = [column for column in df if column not in META and pd.api.types.is_numeric_dtype(df[column])]
    x, y, groups = df[features], df["fault_id"], df["group"]
    cv = StratifiedGroupKFold(n_splits=3, shuffle=True, random_state=42)
    actual, predicted = [], []
    for train, test in cv.split(x, y, groups):
        model = RandomForestClassifier(
            n_estimators=500, max_features="sqrt", min_samples_leaf=2,
            class_weight="balanced_subsample", random_state=42, n_jobs=-1,
        ).fit(x.iloc[train], y.iloc[train])
        actual.extend(y.iloc[test])
        predicted.extend(model.predict(x.iloc[test]))

    report = (
        "V3 relabelled-dataset grouped validation (3 folds)\n"
        f"Accuracy: {accuracy_score(actual, predicted) * 100:.2f}%\n"
        f"Balanced accuracy: {balanced_accuracy_score(actual, predicted) * 100:.2f}%\n\n"
        + classification_report(actual, predicted, zero_division=0)
    )
    print(report)
    REPORT_OUTPUT.write_text(report)
    final_model = RandomForestClassifier(
        n_estimators=500, max_features="sqrt", min_samples_leaf=2,
        class_weight="balanced_subsample", random_state=42, n_jobs=-1,
    ).fit(x, y)
    joblib.dump({"model": final_model, "features": features, "labels": sorted(y.unique())}, MODEL_OUTPUT)
    print(f"Saved model: {MODEL_OUTPUT}")


if __name__ == "__main__":
    main()
