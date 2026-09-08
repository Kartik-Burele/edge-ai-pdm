import pandas as pd
import numpy as np

from sklearn.model_selection import StratifiedGroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    balanced_accuracy_score
)
from sklearn.inspection import permutation_importance
import joblib


# ============================================================
# SETTINGS
# ============================================================

INPUT = r"C:\Users\40036626\Documents\Kartik\Code_v1\PDM_V1\log_file\output290826\ml_dataset.csv"

MODEL_OUTPUT = r"C:\Users\40036626\Documents\Kartik\Code_v1\PDM_V1\log_file\output290826\motor_fault_model.pkl"

LABELS = [
    "HEALTHY",
    "F1",
    "F2",
    "F3",
    "F4"
]


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT)

print("\nDataset loaded")
print("Rows:", len(df))


# ============================================================
# IDENTIFY FEATURES
# ============================================================

META = [
    "dataset_type",
    "fault_id",
    "fault_description",
    "file",
    "iteration",
    "segment",
    "window",
    "start_time_s",
    "group"
]

feature_cols = [
    c for c in df.columns
    if c not in META
    and pd.api.types.is_numeric_dtype(df[c])
]

X = df[feature_cols]
y = df["fault_id"]
groups = df["group"]


print("Features:", len(feature_cols))
print("Groups:", groups.nunique())


# ============================================================
# MODEL
# ============================================================

model = RandomForestClassifier(
    n_estimators=500,
    max_features="sqrt",
    min_samples_leaf=2,
    class_weight="balanced_subsample",
    random_state=42,
    n_jobs=-1
)


# ============================================================
# GROUPED CROSS VALIDATION
# ============================================================

cv = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

all_true = []
all_pred = []

print("\nRunning grouped 5-fold cross validation...")

for fold, (train_idx, test_idx) in enumerate(
    cv.split(X, y, groups),
    start=1
):

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    all_true.extend(y_test)
    all_pred.extend(pred)

    acc = accuracy_score(y_test, pred)

    print(
        f"Fold {fold}: "
        f"{acc * 100:.2f}%"
    )


# ============================================================
# OVERALL RESULTS
# ============================================================

accuracy = accuracy_score(
    all_true,
    all_pred
)

balanced_accuracy = balanced_accuracy_score(
    all_true,
    all_pred
)

print("\n========================================")
print("FINAL CROSS-VALIDATION RESULTS")
print("========================================")

print(
    f"Accuracy: "
    f"{accuracy * 100:.2f}%"
)

print(
    f"Balanced Accuracy: "
    f"{balanced_accuracy * 100:.2f}%"
)


print("\nClassification Report:")

print(
    classification_report(
        all_true,
        all_pred,
        labels=LABELS,
        zero_division=0
    )
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    all_true,
    all_pred,
    labels=LABELS
)

print("\nConfusion Matrix")
print(
    pd.DataFrame(
        cm,
        index=LABELS,
        columns=LABELS
    )
)


# ============================================================
# TRAIN FINAL MODEL ON ALL DATA
# ============================================================

print("\nTraining final model on complete dataset...")

model.fit(X, y)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

importance = pd.DataFrame({
    "feature": feature_cols,
    "importance": model.feature_importances_
})

importance = importance.sort_values(
    "importance",
    ascending=False
)

print("\nTop 20 features:")

print(
    importance.head(20).to_string(
        index=False
    )
)


importance.to_csv(
    MODEL_OUTPUT.replace(
        ".pkl",
        "_feature_importance.csv"
    ),
    index=False
)


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    {
        "model": model,
        "features": feature_cols,
        "labels": LABELS
    },
    MODEL_OUTPUT
)

print("\n========================================")
print("MODEL SAVED")
print("========================================")

print(MODEL_OUTPUT)
