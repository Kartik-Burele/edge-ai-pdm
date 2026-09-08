# Enhanced Predictive Maintenance (PDM) Pipeline

A modular, production-ready predictive maintenance system for laboratory DC motors using vibration, current, and rotational speed telemetry.

---

## 1. What's Improved in `pdm_enhanced/`

| Problem in Previous Iterations | Enhanced Pipeline Solution |
| :--- | :--- |
| **Transient Class Sparsity (V3)**: Isolate short fault events without losing training samples | **Adaptive Sliding Windowing**: Employs 75% overlap (0.25s hop) over active fault intervals while using standard 1.0s non-overlapping windows for steady-state baseline. |
| **Spectral Frequency Smearing**: Fixed FFT bins vary with motor speed | **Rotational Order Tracking**: Synchronizes $1\times, 2\times, 3\times$ harmonic extraction with instantaneous shaft rotational speed ($f_0 = \text{RPM} / 60$). |
| **Missing Electrical Coupling**: Current only treated as basic statistics | **Electromechanical Physical Features**: Computes $dI/dt$, $d\omega/dt$, and torque-efficiency proxy ratio ($\text{RPM} / \text{Current}$). |
| **Excessive Features on Microcontroller**: 40+ collinear features | **Feature Selection & Domain Pruning**: Reduced to **12 compact, uncorrelated features** tailored for embedded microcontrollers. |
| **Overconfident Edge False Alarms**: RF forced classifications | **Continuous Health Index (0–100%) & Anomaly Gate**: Standardized health degradation metric and Isolation Forest out-of-distribution filter. |
| **1-Second Firmware Latency**: Buffer cleared every 200 samples | **Rolling Circular Ring Buffer**: 200-sample history with **250 ms rolling inference** (4 updates/sec). |

---

## 2. Directory Layout

```
pdm_enhanced/
├── README.md
├── data/
│   ├── event_manifest.csv            # Ground truth fault intervals
│   ├── master_features.csv           # All windowed feature extractions
│   ├── ml_dataset.csv                # Finite numeric ML dataset
│   ├── dataset_summary.csv           # Class distribution breakdown
│   └── feature_list.txt              # All candidate feature names
├── data_processing/
│   ├── __init__.py
│   ├── feature_extractor.py          # Time-domain, spectral, order tracking & electromechanical features
│   └── dataset_builder.py            # Adaptive sliding window builder & validator
├── models/
│   ├── __init__.py
│   ├── anomaly_detector.py           # Isolation Forest healthy baseline novelty gate
│   ├── health_index.py               # Continuous 0-100% Health Index & operating state
│   ├── train_and_evaluate.py         # 5-fold Stratified Group-aware CV & model exporter
│   └── saved_models/
│       ├── pdm_fault_model.pkl       # Serialized compact Random Forest model
│       ├── anomaly_detector.pkl      # Serialized baseline anomaly detector
│       ├── feature_importance.csv    # Feature importance rankings
│       ├── confusion_matrix.csv      # Out-of-fold confusion matrix
│       └── validation_report.txt     # Complete cross-validation report
├── inference/
│   ├── __init__.py
│   └── predict_motor.py              # CLI & streaming inference with JSON telemetry
├── embedded/
│   ├── export_c_header.py            # Transpiles scikit-learn RF to C++ code
│   ├── platformio.ini                # ESP32-S3 PlatformIO project definition
│   ├── include/
│   │   └── pdm_model.h               # Generated static C++ decision forest
│   └── src/
│       └── main.cpp                  # 200Hz sampling, 250ms rolling ring buffer, auto zero-calibration
└── tests/
    ├── __init__.py
    ├── test_feature_extractor.py     # Unit tests for signal processing functions
    ├── test_inference.py             # Integration tests for inference engine
    └── test_embedded_parity.py       # Python vs C++ decision logic equivalence test
```

---

## 3. Quickstart & Usage Guide

### A. Run Automated Unit & Integration Tests
```bash
PYTHONPATH=. python3 -m unittest discover -s pdm_enhanced/tests
```

### B. Rebuild Dataset with Adaptive Sliding Windows
```bash
PYTHONPATH=. python3 pdm_enhanced/data_processing/dataset_builder.py
```

### C. Train and Evaluate Models (5-Fold Stratified Group CV)
```bash
PYTHONPATH=. python3 pdm_enhanced/models/train_and_evaluate.py
```

### D. Run Diagnostics & Inference on a Raw Recording
Analyze any raw CSV recording with rolling 250ms windows:
```bash
PYTHONPATH=. python3 pdm_enhanced/inference/predict_motor.py log_file/demo_newcoupler1.csv
```

To export per-window predictions to CSV:
```bash
PYTHONPATH=. python3 pdm_enhanced/inference/predict_motor.py log_file/demo_newcoupler1.csv --output-csv predictions.csv
```

To output raw JSON telemetry (for IoT / MQTT streaming):
```bash
PYTHONPATH=. python3 pdm_enhanced/inference/predict_motor.py log_file/demo_newcoupler1.csv --json
```

### E. Export C++ Header & Flash ESP32-S3 Firmware
Export latest model weights to C++:
```bash
PYTHONPATH=. python3 pdm_enhanced/embedded/export_c_header.py
```

Compile and upload firmware to ESP32-S3:
```bash
pio run -d pdm_enhanced/embedded -t upload
pio device monitor -d pdm_enhanced/embedded --baud 115200
```

---

## 4. Key Performance Metrics (5-Fold Grouped Cross-Validation)

* **Overall Accuracy:** `90.73%`
* **Balanced Accuracy:** `80.24%`
* **Macro F1:** `0.766`
* **Validation Strategy:** Stratified Group K-Fold split strictly across 45 independent recordings (`group = file`), ensuring zero cross-window training leakage.

| Class | Fault Description | Precision | Recall | F1-Score | Support |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **HEALTHY** | Normal Operating Envelope | **0.96** | **0.93** | **0.95** | 910 |
| **F1** | Repeat Load Step (0.4A–0.8A) | **0.63** | **0.97** | **0.77** | 68 |
| **F2** | Step Load Increase (0.3A–1.0A) | **0.63** | **0.57** | **0.60** | 21 |
| **F3** | Current Spike (0.2A–1.0A) | **0.66** | **0.84** | **0.74** | 32 |
| **F4** | Undervoltage (9V–12V @ 1A) | **0.89** | **0.69** | **0.78** | 91 |

---

## 5. Embedded Firmware LED Status Codes

| Color | LED State | Class Index | Operating Condition |
| :--- | :--- | :---: | :--- |
| 🟢 **Green** | Steady | `4` | **HEALTHY** / Nominal Operating State |
| 🟠 **Amber** | Active | `0` | **F1**: Repeat Load Step Transient |
| 🟡 **Yellow** | Active | `1` | **F2**: Step Load Increase |
| 🟣 **Purple** | Active | `2` | **F3**: Load Current Spike |
| 🔴 **Red** | Active | `3` | **F4**: Undervoltage Alarm |
| 🔵 **Blue** | Steady / Blinking | — | Sensor Initialization / Zero-Current Calibration / RPM Low |
