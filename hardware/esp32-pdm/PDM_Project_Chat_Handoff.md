# Predictive Maintenance Motor Fault Detection --- Chat Handoff

## Project objective

Build a laboratory predictive-maintenance system for a DC motor using an
ESP32, accelerometer (Ax/Ay/Az), ACS712/current ADC, encoder RPM, a 12 V
PSU, a second mechanically coupled DC motor, and a programmable
Scientific DC electronic load.

Goal: classify the monitored motor as **HEALTHY, F1, F2, F3, or F4**
using sensor-derived features and a machine-learning model.

## Current hardware setup

-   Motor 1: monitored motor, powered from 12 V DC PSU.
-   Motor 2: mechanically coupled shaft-to-shaft; used as generator/load
    side.
-   Scientific programmable DC electronic load connected to Motor 2
    terminals.
-   ESP32 reads accelerometer, ACS712 ADC and encoder RPM.
-   Tachometer was used to independently verify firmware RPM; readings
    were reported as closely matching.
-   A 100 ohm, 100 W rheostat was also available and previously tested.
-   Current setup is intended to remain mechanically intact while
    electrical faults are induced through the programmable load.

## Healthy experiment

Healthy CC load points: **0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
1.0 and 2.0 A.**

Three independent healthy iterations were recorded: - 11 load points × 3
iterations = **33 healthy CSV files** - Each recording was approximately
**20 seconds**.

Typical manually recorded fields: - iteration - load_A -
load_voltage_V - psu_current_A - load_power_W - supply_voltage_V

Example healthy operating data showed supply voltage at 12 V and
increasing load/PSU current as CC load increased.

## Firmware / CSV format

Encoder RPM was added to the ESP32 firmware.

Raw CSV columns: `timestamp_ms, ax, ay, az, acs_adc, rpm`

The RPM was verified with a tachometer.

Some RPM startup/invalid samples existed, so RPM
preprocessing/diagnostic fields were added.

## Feature extraction

Sampling frequency: `FS = 200 Hz`

Window: `1 second = 200 samples`

Accelerometer features per axis: - mean - std - RMS - peak -
peak-to-peak - crest factor

Acceleration magnitude: - RMS - std - peak - peak-to-peak

ACS712: - mean - std - RMS - min - max - peak-to-peak

FFT/spectral features from acceleration magnitude: - dominant
frequency - dominant amplitude - spectral energy - spectral centroid

RPM features include: - rpm_mean - rpm_min - rpm_median - rpm_max and
RPM diagnostic fields: - rpm_raw_mean - rpm_raw_median -
rpm_invalid_samples - rpm_valid_fraction - rpm_invalid_fraction

The diagnostic RPM fields are excluded from ML features.

## Fault experiments

Mechanical fault attempts used approximately 1--2 mm printed shims
under/at the edge of Motor 2's bracket. The resulting changes were not
sufficiently strong/reproducible, so mechanical fault collection was
deferred.

Electrical fault scenarios were therefore prioritized using the
programmable DC electronic load.

Four fault types were recorded, with approximately three recordings
each:

-   **F1:** repeat load step --- `repeat_cc_0.4_0.8A`
-   **F2:** step load increase --- `stepup_cc_0.3_1A`
-   **F3:** current spike --- `spike_cc_0.2_1A`
-   **F4:** undervoltage --- `UV_cc_1A_9V_12V`

Total fault files = **12**.

Total independent recording groups/files = **33 healthy + 12 fault =
45**.

## ML dataset

`prepare_ml_dataset.py` creates: `ml_dataset.csv`

Final dataset: - **963 one-second windows** - **40 ML features** - **45
independent CSV groups** - Healthy: **713 windows** - F1: **67** - F2:
**62** - F3: **61** - F4: **60**

Important: individual windows from the same CSV are correlated.
Therefore grouped train/test validation is required to avoid leakage.

The preparation script had a bug because `fault_id` was already in
`META` but was also added again. This caused:
`ValueError: Grouper for 'fault_id' not 1-dimensional`

Correct construction:

``` python
out = df.loc[mask, META + feature_cols].copy()
```

not:

``` python
META + ["fault_id"] + feature_cols
```

## Current Random Forest

`train_model.py` uses:

``` python
RandomForestClassifier(
    n_estimators=500,
    max_features="sqrt",
    min_samples_leaf=2,
    class_weight="balanced_subsample",
    random_state=42,
    n_jobs=-1
)
```

Validation:

``` python
StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)
```

Grouping variable: `group = file`

## Actual current ML result

The latest training output was:

-   Rows: **963**
-   Features: **40**
-   Groups: **45**

5-fold grouped CV: - Fold 1: **99.48%** - Fold 2: **96.37%** - Fold 3:
**96.35%** - Fold 4: **97.93%** - Fold 5: **93.75%**

Overall: - **Accuracy: 96.78%** - **Balanced Accuracy: 92.16%** -
**Macro F1: \~0.93** - **Weighted F1: \~0.97**

Classification report:

  Class       Precision   Recall     F1   Support
  --------- ----------- -------- ------ ---------
  HEALTHY          0.98     0.99   0.98       713
  F1               0.98     0.88   0.93        67
  F2               0.92     0.95   0.94        62
  F3               0.90     0.87   0.88        61
  F4               0.93     0.92   0.92        60

Confusion matrix:

  Actual  Predicted     HEALTHY   F1   F2   F3   F4
  ------------------- --------- ---- ---- ---- ----
  HEALTHY                   706    0    0    6    1
  F1                          5   59    3    0    0
  F2                          2    0   59    0    1
  F3                          4    0    2   53    2
  F4                          4    1    0    0   55

## Current feature importance

Top features from the final Random Forest:

1.  `az_mean` --- 0.080731
2.  `rpm_min` --- 0.076536
3.  `ay_std` --- 0.059683
4.  `ay_rms` --- 0.054040
5.  `rpm_median` --- 0.053092
6.  `ax_crest` --- 0.049054
7.  `ax_rms` --- 0.047352
8.  `ay_p2p` --- 0.047132
9.  `ax_std` --- 0.044260
10. `rpm_max` --- 0.040419
11. `acs_rms` --- 0.027810
12. `acs_mean` --- 0.026460
13. `rpm_mean` --- 0.026094
14. `acs_min` --- 0.025691
15. `spectral_energy` --- 0.024488
16. `ax_peak` --- 0.024007
17. `ay_peak` --- 0.021746
18. `ax_p2p` --- 0.020768
19. `acc_mag_p2p` --- 0.019763
20. `az_std` --- 0.019036

RPM is clearly represented among important features: `rpm_min` rank 2,
`rpm_median` rank 5, `rpm_max` rank 10, `rpm_mean` rank 13.

An earlier approximate comparison suggested that adding RPM improved
overall performance slightly and particularly helped F4 undervoltage
detection, but that comparison should be reproduced with the exact
current pipeline before being used as a formal benchmark.

## F4 observation

Earlier analysis indicated approximately: - Healthy RPM mean: \~2893 -
Healthy RPM std: \~4.6 - Healthy RPM peak-to-peak: \~33 - F4 RPM mean:
\~2686 - F4 RPM std: \~292 - F4 RPM peak-to-peak: \~1276

This indicates a strong RPM signature under the undervoltage experiment.

## Saved model

Model file: `motor_fault_model.pkl`

Path:
`C:\Users\40036626\Documents\Kartik\Code_v1\PDM_V1\log_file\output290826\motor_fault_model.pkl`

It contains:

``` python
{
    "model": model,
    "features": feature_cols,
    "labels": LABELS
}
```

Labels:

``` python
["HEALTHY", "F1", "F2", "F3", "F4"]
```

## Immediate next task

Do **not** collect more data unless absolutely necessary.

Build an inference script, preferably `predict_motor.py`, that: 1. Takes
a new raw CSV. 2. Splits it into the same 1-second windows. 3.
Calculates exactly the same 40 features as training. 4. Loads
`motor_fault_model.pkl`. 5. Uses the stored feature list to enforce
exact feature ordering. 6. Produces per-window prediction. 7. Produces
model probability/confidence for each window. 8. Aggregates the windows
into a final motor condition using a defensible majority/weighted vote.

Desired demonstration:

``` text
MOTOR PREDICTION

Windows analyzed: 20

Final prediction:
F4 - Undervoltage

Confidence:
[calculated probability, not invented]
```

## Remaining work in priority order

### Priority 1

Make `predict_motor.py` work on existing recordings.

### Priority 2

Test on existing recordings representing: - Healthy - F1 - F2 - F3 - F4

Prefer recordings not used in the particular training fit if a true
holdout is available.

### Priority 3

Generate: - confusion matrix - feature importance plot - class-wise F1
plot

### Priority 4

Test feature reduction: - 40 features - top 20 - top 15 - top 10

Compare accuracy, balanced accuracy, macro F1, class recalls, model size
and inference time.

### Priority 5

Reproduce a strict comparison: - Model A: vibration + ACS712 - Model B:
vibration + ACS712 + RPM

Use identical grouped folds/random seed.

## Important technical caveats

-   963 windows are not 963 independent experiments.
-   There are only 45 independent CSV recordings.
-   Each fault class has only about 3 independent recordings.
-   Group-aware validation is essential.
-   The dataset is class-imbalanced: 713 Healthy vs 250 fault windows.
-   RPM startup/invalid readings must be handled consistently.
-   Training and inference feature extraction must be identical.
-   Do not use operating-condition metadata as ML features if it leaks
    the fault condition.
-   Do not claim 96.78% as universal real-world accuracy.
-   Defensible wording: "Using 5-fold group-aware cross-validation on
    963 one-second windows from 45 independent recordings, the Random
    Forest achieved 96.78% classification accuracy, 92.16% balanced
    accuracy and approximately 0.93 macro F1."
-   The experiments are controlled laboratory fault scenarios, so
    generalization should not be overstated.

## Recommended final system architecture

Motor → Accelerometer + ACS712 + Encoder → ESP32 data logger → CSV →
feature extraction → vibration/current/RPM features → Random Forest →
HEALTHY / F1 / F2 / F3 / F4 → confidence + final condition

## Current project status

The project has successfully reached:

**Hardware → Data acquisition → Healthy data → Controlled fault data →
RPM integration → Feature extraction → ML dataset → Grouped Random
Forest training**

Current headline result:

**96.78% grouped cross-validation accuracy**

The next milestone is:

**Raw CSV → feature extraction → trained model → fault classification +
confidence**

This is the current point from which the next model should continue.
