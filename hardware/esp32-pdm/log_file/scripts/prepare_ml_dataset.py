import pandas as pd
import numpy as np

INPUT = r'C:\Users\40036626\Documents\Kartik\Code_v1\PDM_V1\log_file\output290826\master_features_with_rpm.csv'
OUTPUT = r'C:\Users\40036626\Documents\Kartik\Code_v1\PDM_V1\log_file\output290826\ml_dataset.csv'

# ============================================================
# LOAD MASTER DATASET
# ============================================================

df = pd.read_csv(INPUT)

# Remove duplicate column names from input
df = df.loc[:, ~df.columns.duplicated()]

# ============================================================
# COLUMN DEFINITIONS
# ============================================================

META = [
    "dataset_type",
    "fault_id",
    "fault_description",
    "file",
    "iteration",
    "segment",
    "window",
    "start_time_s"
]

OPERATING = [
    "load_A",
    "load_voltage_V",
    "psu_current_A",
    "load_power_W",
    "supply_voltage_V"
]

# RPM diagnostic columns that we do NOT want
# as ML features
DROP = META + OPERATING + [
    "rpm_raw_mean",
    "rpm_raw_median",
    "rpm_invalid_samples",
    "rpm_valid_fraction",
    "rpm_invalid_fraction"
]

# ============================================================
# SELECT ML FEATURES
# ============================================================

feature_cols = [
    c for c in df.columns
    if c not in DROP
    and pd.api.types.is_numeric_dtype(df[c])
]

print("\nSelected ML features:")
for feature in feature_cols:
    print("  ", feature)

print("\nNumber of features:", len(feature_cols))

# ============================================================
# VALIDITY MASK
# ============================================================

mask = df["fault_id"].notna()

# Remove rows containing NaN / Inf in ML features
mask &= np.isfinite(
    df[feature_cols].to_numpy()
).all(axis=1)

# ============================================================
# CREATE ML DATASET
# ============================================================
# IMPORTANT:
# fault_id is already present inside META.
# Do NOT add ["fault_id"] again.

out = df.loc[
    mask,
    META + feature_cols
].copy()

# ============================================================
# GROUP IDENTIFIER
# ============================================================
# All windows belonging to the same original CSV
# must remain in the same train/test group.

out["group"] = out["file"]

# ============================================================
# SAVE
# ============================================================

out.to_csv(
    OUTPUT,
    index=False
)

# ============================================================
# DATASET SUMMARY
# ============================================================

print("\n========================================")
print("ML DATASET CREATED")
print("========================================")

print("Saved:", OUTPUT)
print("Rows:", len(out))
print("Features:", len(feature_cols))
print("Groups/files:", out["group"].nunique())

print("\nFault distribution:")
print(out["fault_id"].value_counts())

print("\nDataset type distribution:")
print(out["dataset_type"].value_counts())

print("\nGroups per fault:")
print(
    out.groupby("fault_id")["group"]
       .nunique()
)

print("\nFirst 5 rows:")
print(out.head())
