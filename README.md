# Edge AI Predictive Maintenance (PDM) System

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Version](https://img.shields.io/badge/Version-2.0.0-blue)
![Platform](https://img.shields.io/badge/Platform-ESP32--S3-orange)
![Framework](https://img.shields.io/badge/Framework-Arduino%20%7C%20PlatformIO-blue)
![ML](https://img.shields.io/badge/ML-Random%20Forest-green)

A complete end-to-end **Edge AI Predictive Maintenance (PDM)** system for real-time motor condition monitoring, machine-learning-based fault classification, embedded inference, and wireless dashboard visualization.

The project combines **sensor data acquisition, feature engineering, machine learning, embedded Edge AI inference, and Wi-Fi-based monitoring** into a single predictive-maintenance platform.

Developed as part of the **M.Tech in Applied AI and Communications program at VNIT**.

---

## 📖 Overview

Predictive maintenance aims to identify abnormal machine behavior before it develops into a major failure.

This project implements a laboratory-scale predictive-maintenance system for a DC motor using an **ESP32-S3 microcontroller** as the edge-processing device.

The system continuously measures:

- Motor vibration using an **MPU6050 accelerometer**
- Motor current using an **ACS712 current sensor**
- Motor speed using an **optical encoder**

The acquired sensor signals are processed locally on the ESP32-S3. Features are extracted from rolling data windows and supplied directly to an embedded **Random Forest classifier**.

The classifier identifies the motor operating condition as one of five classes:

1. **HEALTHY**
2. **F1 – Repeat Load-Step Condition**
3. **F2 – Step Load Increase**
4. **F3 – Current-Spike Condition**
5. **F4 – Undervoltage Condition**

The prediction, confidence, motor speed, current-related information, and other telemetry are then made available through a **Wi-Fi HTTP server** hosted directly on the ESP32-S3.

A browser-based dashboard can connect to the ESP32 over the local network and display the motor condition in real time.

---

# ✨ Features

### Edge AI Inference

- Random Forest machine-learning model embedded directly into the ESP32-S3 firmware.
- No cloud server is required for model inference.
- Prediction is performed locally at the edge.
- Current embedded model contains:
  - **12 input features**
  - **35 decision trees**
  - **5 output classes**

### Multi-Sensor Motor Monitoring

The physical implementation combines:

- MPU6050 accelerometer
- ACS712 current sensor
- Optical encoder for RPM measurement

This allows the model to use vibration, electrical-current, and rotational-speed information simultaneously.

### Real-Time Data Acquisition

- Sampling frequency: **200 Hz**
- Circular buffer: **200 samples**
- One-second rolling analysis window
- ML inference performed every **250 ms**

### Embedded Feature Extraction

The firmware calculates features from the acquired sensor data before passing them to the embedded ML model.

The deployed feature set includes vibration, current, and RPM-related characteristics.

### Wi-Fi Connectivity

The ESP32-S3 connects to the same local network as the monitoring laptop.

The ESP32 hosts an HTTP server that provides:

```text
ESP32-S3
    ↓
Wi-Fi
    ↓
Laptop / Browser
    ↓
Real-Time Dashboard
```

### Built-In Web Dashboard

The dashboard is served directly from the ESP32-S3 firmware.

No separate Streamlit server is required for the physical deployment.

The dashboard displays information such as:

- Current prediction
- Motor health status
- Prediction confidence
- RPM
- RPM trend/slope
- Current change rate
- Temperature
- Real-time telemetry

### JSON API

The ESP32 provides a machine-readable endpoint:

```text
/api/data
```

The endpoint returns the latest prediction and sensor-derived telemetry in JSON format.

### Prediction Smoothing

Temporal prediction smoothing is implemented in the firmware to reduce unstable class transitions caused by individual noisy inference windows.

### Visual Status Indication

The ESP32 uses an RGB NeoPixel status LED to provide a local indication of the detected motor condition.

---

# 🏗️ Overall System Architecture

```text
                    PHYSICAL MOTOR SYSTEM
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
         MPU6050         ACS712       Encoder
       Vibration         Current         RPM
              │             │             │
              └─────────────┼─────────────┘
                            │
                            ▼
                      ESP32-S3
                            │
                    Sensor Acquisition
                            │
                            ▼
                    Feature Extraction
                            │
                            ▼
                 Embedded Random Forest
                       Edge AI Model
                            │
                            ▼
                 Prediction + Confidence
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
        NeoPixel LED                 Wi-Fi Server
                                          │
                                          ▼
                                  Browser Dashboard
```

The complete Edge AI processing pipeline is therefore:

```text
Sensors
   ↓
Data Acquisition
   ↓
Rolling Window
   ↓
Feature Extraction
   ↓
Random Forest Inference
   ↓
Prediction Smoothing
   ↓
Motor Health Classification
   ↓
Wi-Fi
   ↓
Web Dashboard
```

---

# ⚙️ Hardware Implementation

The current physical implementation is based on an:

**ESP32-S3 DevKitC-1**

The ESP32-S3 performs both sensor processing and machine-learning inference locally.

### Sensors

| Component | Purpose |
|---|---|
| MPU6050 | Motor vibration measurement |
| ACS712 | Motor/load current measurement |
| Optical Encoder | Motor RPM measurement |
| NeoPixel | Local motor-status indication |

The experimental setup uses a motor powered from a **12 V DC supply**.

A second mechanically coupled motor and programmable DC electronic load are used to create controlled operating conditions.

---

# 🔌 ESP32-S3 Pin Configuration

The current firmware uses the following pins:

| Function | ESP32-S3 Pin |
|---|---:|
| MPU6050 SDA | GPIO 8 |
| MPU6050 SCL | GPIO 9 |
| ACS712 ADC | GPIO 4 |
| Encoder Index | GPIO 6 |
| RGB Status LED | GPIO 38 |

---

# 📡 Sensor Acquisition

The firmware operates at a sampling frequency of:

```text
200 Hz
```

Each sensor window contains:

```text
200 samples
```

Therefore:

```text
200 samples / 200 Hz = 1 second
```

The firmware uses a circular buffer to continuously maintain the latest one-second window.

ML inference is triggered every:

```text
50 samples
```

which corresponds to:

```text
50 / 200 Hz = 250 ms
```

Therefore, the system continuously evaluates the motor condition using overlapping one-second windows.

---

# 📊 Sensor Data

The raw data acquisition pipeline records:

```text
timestamp_ms
ax
ay
az
acs_adc
rpm
```

Where:

- `ax` = acceleration along X-axis
- `ay` = acceleration along Y-axis
- `az` = acceleration along Z-axis
- `acs_adc` = ACS712 ADC measurement
- `rpm` = motor rotational speed

RPM measurements were independently verified using a tachometer during the experimental data-collection process.

---

# 🧮 Feature Engineering

The machine-learning pipeline initially extracts a larger feature set from the raw sensor recordings.

The training dataset contains:

```text
40 ML features
```

These features include statistical, vibration, electrical-current, spectral, and RPM characteristics.

Examples include:

### Vibration Features

- Mean
- Standard deviation
- RMS
- Peak
- Peak-to-peak
- Crest factor

### Current Features

- Mean
- Standard deviation
- RMS
- Minimum
- Maximum
- Peak-to-peak

### Spectral Features

- Dominant frequency
- Dominant amplitude
- Spectral energy
- Spectral centroid

### RPM Features

- Mean RPM
- Minimum RPM
- Median RPM
- Maximum RPM
- RPM variation

The final embedded model uses a compact **12-feature representation** suitable for microcontroller deployment.

---

# 🤖 Machine Learning Model

The current predictive-maintenance classifier is a:

**Random Forest Classifier**

The training configuration uses:

```text
Number of trees:       500
max_features:          sqrt
min_samples_leaf:      2
class weighting:       balanced_subsample
random_state:          42
```

The model is validated using:

```text
StratifiedGroupKFold
```

with:

```text
5 folds
```

and the **recording file** is used as the grouping variable.

This is important because multiple one-second windows are extracted from the same recording. Randomly splitting individual windows could therefore cause data leakage between training and validation sets.

---

# 🧠 Embedded AI Model

The deployed ESP32-S3 model is a compact embedded Random Forest representation.

Current embedded model:

```text
Input features : 12
Decision trees  : 35
Output classes  : 5
```

The embedded feature vector contains:

```text
1.  rpm_min
2.  rpm_median
3.  rpm_slope_rpm_per_s
4.  rpm_p2p
5.  acs_dI_dt_slope
6.  acs_p2p
7.  az_mean
8.  ay_rms
9.  ay_p2p
10. ax_crest
11. order_2x_energy
12. az_std
```

The generated embedded model is stored in:

```text
hardware/esp32-pdm/include/pdm_model.h
```

The generated model file should not be manually edited.

---

# 🚨 Motor Condition Classes

The current physical implementation uses five classes.

| Class | Description |
|---|---|
| `HEALTHY` | Normal motor operation |
| `F1` | Repeat load-step condition |
| `F2` | Step load increase |
| `F3` | Current-spike condition |
| `F4` | Undervoltage condition |

These classes represent the controlled operating/fault scenarios used during the current laboratory experiments.

They should not be interpreted as universal physical motor-failure categories.

---

# 📚 Dataset

The current experimental dataset contains:

```text
963 one-second windows
40 ML features
45 independent recording groups
```

Class distribution:

| Class | Windows |
|---|---:|
| HEALTHY | 713 |
| F1 | 67 |
| F2 | 62 |
| F3 | 61 |
| F4 | 60 |
| **Total** | **963** |

The dataset was generated from:

```text
33 Healthy recordings
12 Fault recordings
45 Total recordings
```

The healthy recordings were collected across multiple controlled load conditions.

---

# 🧪 Healthy Operating Conditions

Healthy motor data was collected across controlled load points including:

```text
0.1 A
0.2 A
0.3 A
0.4 A
0.5 A
0.6 A
0.7 A
0.8 A
0.9 A
1.0 A
2.0 A
```

Three iterations were collected for the healthy operating conditions.

---

# ⚠️ Controlled Fault Conditions

The current experiments prioritize electrically induced operating abnormalities.

### F1 — Repeat Load Step

```text
repeat_cc_0.4_0.8A
```

### F2 — Step Load Increase

```text
stepup_cc_0.3_1A
```

### F3 — Current Spike

```text
spike_cc_0.2_1A
```

### F4 — Undervoltage

```text
UV_cc_1A_9V_12V
```

Approximately three recordings were collected for each fault scenario.

---

# 📈 Model Validation

The Random Forest was evaluated using **5-fold group-aware cross-validation**.

The results obtained on the current controlled laboratory dataset are:

| Metric | Result |
|---|---:|
| Accuracy | **96.78%** |
| Balanced Accuracy | **92.16%** |
| Macro F1 | **≈ 0.93** |
| Weighted F1 | **≈ 0.97** |

Individual fold accuracies:

```text
Fold 1 : 99.48%
Fold 2 : 96.37%
Fold 3 : 96.35%
Fold 4 : 97.93%
Fold 5 : 93.75%
```

### Class-wise Performance

| Class | Precision | Recall | F1 |
|---|---:|---:|---:|
| HEALTHY | 0.98 | 0.99 | 0.98 |
| F1 | 0.98 | 0.88 | 0.93 |
| F2 | 0.92 | 0.95 | 0.94 |
| F3 | 0.90 | 0.87 | 0.88 |
| F4 | 0.93 | 0.92 | 0.92 |

> **Important:** 96.78% is a group-aware cross-validation result on the current controlled laboratory dataset. It should not be interpreted as universal real-world motor-fault detection accuracy.

There are currently only 45 independent recordings, with approximately three independent recordings for each fault scenario. Additional experiments are required to establish broader generalization.

---

# 🔍 Important Features

Feature-importance analysis identified several important features for classification.

The highest-ranked features include:

```text
1.  az_mean
2.  rpm_min
3.  ay_std
4.  ay_rms
5.  rpm_median
6.  ax_crest
7.  ax_rms
8.  ay_p2p
9.  ax_std
10. rpm_max
```

RPM-derived features are particularly useful for distinguishing operating conditions involving changes in motor speed.

For example, the undervoltage condition produces significant RPM variation compared with healthy operation.

---

# 💻 Embedded Inference Pipeline

The physical ESP32-S3 firmware follows this sequence:

```text
MPU6050 + ACS712 + Encoder
             ↓
       200 Hz Sampling
             ↓
      Circular Buffer
             ↓
      200-Sample Window
             ↓
      Feature Extraction
             ↓
      12-Feature Vector
             ↓
    Embedded Random Forest
             ↓
       Class Prediction
             ↓
   Temporal Smoothing
             ↓
  Health + Confidence
```

Inference is performed directly on the ESP32-S3.

The raw sensor window does **not** need to be uploaded to the cloud for classification.

---

# 🔄 Prediction Smoothing

Individual sensor windows can produce temporary prediction changes because of noise and transient operating conditions.

The firmware therefore applies temporal prediction smoothing before presenting the final motor condition.

This reduces unstable class transitions and produces a more useful real-time health indication.

---

# 📶 Wi-Fi Communication

The ESP32-S3 operates as a Wi-Fi station and connects to the same local network as the monitoring laptop.

After connecting, the firmware prints the ESP32 IP address to the serial monitor.

Example:

```text
WiFi connected
IP address: <ESP32-IP>
```

The dashboard can then be accessed from a browser using:

```text
http://<ESP32-IP>
```

For example:

```text
http://192.168.x.x
```

The exact address depends on the local network.

---

# 🌐 JSON API

The ESP32 provides a JSON API through:

```text
/api/data
```

The API exposes the latest machine-learning prediction and telemetry.

The information includes values such as:

```text
prediction
health
confidence
rpm
rpm slope
current dI/dt
temperature
```

This allows external applications to consume the Edge AI results without modifying the embedded inference system.

---

# 📊 Real-Time Web Dashboard

The current physical system includes an HTTP dashboard directly inside the ESP32 firmware.

```text
Laptop Browser
       │
       │ HTTP
       ▼
   ESP32-S3
       │
       ▼
 /api/data
       │
       ▼
 Current AI Prediction
```

The browser periodically requests updated data from the ESP32.

Current polling interval:

```text
500 ms
```

The dashboard provides real-time visualization of the motor's condition and telemetry.

---

# 💡 Local Status Indication

The ESP32-S3 also provides local visual feedback using a NeoPixel RGB LED.

The LED is connected to:

```text
GPIO 38
```

This provides an immediate physical indication of the current system state without requiring a laptop.

---

# 📂 Project Structure

The repository contains both the original software/simulation work and the new physical ESP32-S3 Edge AI implementation.

```text
edge-ai-pdm/
│
├── DUDU-BLDC/
│   └── DUDU-BLDC/
│
├── Docs/
│
├── bldc_pdm/
│
├── data/
│
├── models/
│
├── src/
│
├── tools/
│
├── hardware/
│   └── esp32-pdm/
│       │
│       ├── dataset_v3/
│       │   ├── build_dataset_v3.py
│       │   ├── train_model_v3.py
│       │   ├── event_label_manifest_v3.csv
│       │   ├── master_features_relabelled_v3.csv
│       │   └── ml_dataset_v3.csv
│       │
│       ├── embedded_model_v2/
│       │
│       ├── include/
│       │   └── pdm_model.h
│       │
│       ├── lib/
│       │
│       ├── log_file/
│       │
│       ├── pdm_enhanced/
│       │
│       ├── src/
│       │   └── main.cpp
│       │
│       ├── test/
│       │
│       ├── PDM_Project_Chat_Handoff.md
│       │
│       └── platformio.ini
│
├── IMPLEMENTATION_LOGS.md
├── README.md
├── VIVA_PREP.md
├── findings.md
├── progress.md
├── task_plan.md
├── gemini.md
└── pyproject.toml
```

---

# 🧪 Dataset Version 3

The `dataset_v3` directory contains the updated dataset-generation and model-training pipeline.

The updated labeling strategy distinguishes:

- Healthy baseline/recovery windows
- F1 event windows
- F2 event windows
- F3 event windows
- F4 event windows

The main scripts are:

```text
dataset_v3/build_dataset_v3.py
dataset_v3/train_model_v3.py
```

From the `hardware/esp32-pdm` directory:

```bash
python dataset_v3/build_dataset_v3.py
python dataset_v3/train_model_v3.py
```

---

# ⚙️ Embedded Model Version 2

The repository also contains:

```text
hardware/esp32-pdm/embedded_model_v2/
```

This development version focuses on a compact Random Forest deployment for ESP32-based inference.

The embedded-model development explored reducing the number of trees while retaining vibration, RPM, and current information.

---

# 🔨 ESP32-S3 Setup

The physical deployment uses:

- ESP32-S3 DevKitC-1
- Arduino framework
- PlatformIO
- Adafruit MPU6050 library
- Adafruit NeoPixel library

The PlatformIO configuration is located at:

```text
hardware/esp32-pdm/platformio.ini
```

---

# 🚀 Build and Upload the Firmware

Navigate to the hardware project:

```bash
cd hardware/esp32-pdm
```

Build the firmware:

```bash
pio run
```

Upload it to the ESP32-S3:

```bash
pio run --target upload
```

Open the serial monitor:

```bash
pio device monitor --baud 115200
```

The serial monitor operates at:

```text
115200 baud
```

---

# 📡 Running the Physical Dashboard

After flashing the firmware:

1. Power the ESP32-S3.
2. Ensure the Wi-Fi credentials configured in the firmware correspond to the local network.
3. Open the serial monitor.
4. Wait for the Wi-Fi connection.
5. Note the IP address printed by the ESP32.
6. Connect the laptop to the **same Wi-Fi network**.
7. Open the ESP32 IP address in a browser.

For example:

```text
http://192.168.x.x
```

The dashboard is served directly by the ESP32-S3.

---

# 🔐 Wi-Fi Security

**Do not commit real Wi-Fi passwords to the public GitHub repository.**

The Wi-Fi credentials in the firmware should be replaced with placeholders or moved to a local configuration mechanism that is excluded from Git.

If an actual Wi-Fi password has already been committed to a public repository, it should be changed.

---

# 🖥️ Original Digital Twin / Simulation

The repository also retains the earlier software-based predictive-maintenance and simulation components.

These components were developed before the physical ESP32-S3 implementation and provide a software environment for:

- Data processing
- Machine-learning experimentation
- Digital-twin visualization
- ESP32 simulation
- Model evaluation

Therefore, the repository contains both:

```text
Software / Simulation
        +
Physical Edge AI
```

The physical ESP32-S3 implementation is now the primary real-time Edge AI deployment.

---

# 🔬 Development Phases

## Phase 1 — Data Engineering

- Defined raw sensor data schema.
- Collected motor sensor recordings.
- Added vibration, current, and RPM measurements.
- Developed preprocessing and windowing.
- Added RPM diagnostics and validation.

## Phase 2 — Experimental Dataset

- Collected healthy operating data.
- Collected controlled fault-condition data.
- Added electrical fault scenarios.
- Created grouped one-second ML windows.
- Developed updated dataset labeling.

## Phase 3 — Feature Engineering

- Developed vibration features.
- Developed current features.
- Developed spectral features.
- Added RPM features.
- Evaluated feature importance.
- Reduced the feature set for embedded deployment.

## Phase 4 — Machine Learning

- Trained Random Forest models.
- Implemented group-aware validation.
- Evaluated accuracy, balanced accuracy, precision, recall, and F1.
- Selected a compact model suitable for embedded inference.

## Phase 5 — ESP32-S3 Deployment

- Integrated MPU6050.
- Integrated ACS712.
- Integrated optical encoder.
- Implemented 200 Hz acquisition.
- Implemented circular buffering.
- Implemented embedded feature extraction.
- Integrated Random Forest inference.
- Added prediction smoothing.

## Phase 6 — Wireless Monitoring

- Added Wi-Fi connectivity.
- Added HTTP server.
- Added `/api/data` JSON endpoint.
- Added browser dashboard.
- Added real-time telemetry visualization.
- Added local NeoPixel status indication.

---

# 🧩 Simulation vs Physical Edge AI

The project has evolved from a software-based predictive-maintenance prototype into a physical Edge AI system.

### Earlier architecture

```text
Sensor / Simulated Data
        ↓
Python
        ↓
Feature Extraction
        ↓
ML Model
        ↓
Streamlit Dashboard
```

### Current physical architecture

```text
Motor
  ↓
MPU6050 + ACS712 + Encoder
  ↓
ESP32-S3
  ↓
Feature Extraction
  ↓
Embedded Random Forest
  ↓
Prediction
  ↓
Wi-Fi
  ↓
Browser Dashboard
```

The key difference is that the current system performs **machine-learning inference directly on the ESP32-S3** rather than depending on a laptop or cloud server.

---

# 📌 Current System Summary

| Parameter | Current Implementation |
|---|---|
| Edge Device | ESP32-S3 DevKitC-1 |
| Framework | Arduino |
| Build System | PlatformIO |
| Accelerometer | MPU6050 |
| Current Sensor | ACS712 |
| Speed Sensor | Optical Encoder |
| Sampling Rate | 200 Hz |
| Window Size | 200 samples |
| Window Duration | 1 second |
| Inference Interval | 250 ms |
| ML Algorithm | Random Forest |
| Embedded Trees | 35 |
| Embedded Features | 12 |
| ML Dataset Features | 40 |
| Classes | 5 |
| Recording Groups | 45 |
| ML Windows | 963 |
| CV Accuracy | 96.78% |
| Balanced Accuracy | 92.16% |
| Macro F1 | ≈ 0.93 |
| Communication | Wi-Fi |
| Dashboard | ESP32-hosted Web Dashboard |
| API | `/api/data` |

---

# ⚠️ Limitations

The current system is a **controlled laboratory prototype**.

Important limitations include:

- Only 45 independent recordings are currently available.
- Each fault class has approximately three independent recordings.
- The dataset contains substantially more healthy windows than fault windows.
- Multiple windows originate from the same recording.
- Mechanical fault experiments were not sufficiently reproducible and therefore the current dataset emphasizes controlled electrical/operational abnormalities.
- The current fault classes represent experimental operating scenarios rather than a complete taxonomy of real motor failures.
- Additional motors, operating conditions, loads, and fault severities are required to establish generalization.
- The reported 96.78% accuracy should not be interpreted as universal real-world performance.

---

# 🔮 Future Work

Future development can include:

- Increasing the number of independent motor recordings.
- Testing multiple motors.
- Collecting additional fault severities.
- Adding reproducible mechanical fault conditions.
- Testing additional motor speeds and loads.
- Comparing different ML algorithms.
- Reducing the number of input features.
- Optimizing RAM and flash usage.
- Measuring exact ESP32 inference latency.
- Measuring energy consumption.
- Adding MQTT/cloud connectivity where required.
- Adding long-term health-index estimation.
- Remaining Useful Life (RUL) estimation.
- Automated maintenance alerts.
- Improved dashboard visualization.
- Edge-to-cloud fleet monitoring.

---

# 📚 Documentation

Additional project documentation is available in:

```text
IMPLEMENTATION_LOGS.md
VIVA_PREP.md
PDM_Project_Chat_Handoff.md
findings.md
progress.md
task_plan.md
```

The physical ESP32-S3 implementation is documented under:

```text
hardware/esp32-pdm/
```

---

# 🎓 Academic Context

The project demonstrates the complete lifecycle of an Edge AI predictive-maintenance system:

```text
Data Acquisition
       ↓
Data Preprocessing
       ↓
Feature Engineering
       ↓
Machine Learning
       ↓
Model Validation
       ↓
Model Optimization
       ↓
Embedded Deployment
       ↓
Real-Time Edge Inference
       ↓
Wireless Monitoring
```

The project therefore combines concepts from:

- Artificial Intelligence
- Machine Learning
- Edge Computing
- Embedded Systems
- IoT
- Predictive Maintenance
- Signal Processing
- Industrial Condition Monitoring

---

# 👨‍💻 Author

**Kartik Burele**

M.Tech in Applied AI and Communications  
VNIT

---

# 📜 License

This project is intended for academic, research, and educational purposes.
