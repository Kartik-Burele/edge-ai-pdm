# Edge AI Predictive Maintenance (PDM) System

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![Platform](https://img.shields.io/badge/Platform-ESP32%20%7C%20Streamlit-orange)

A complete end-to-end Machine Learning pipeline for Predictive Maintenance on Edge Devices. Developed for the M.Tech in Applied AI and Communications program at VNIT.

## 📖 Overview

This project demonstrates the deployment of highly efficient machine learning models directly onto resource-constrained edge devices (Microcontrollers) to monitor industrial motor health. The system analyzes vibration and temperature telemetry to detect and classify 4 distinct operational states:
1. **Normal Operation**
2. **Ball Defect**
3. **Inner Race Fault**
4. **Outer Race Fault**

By predicting structural faults early, the system provides actionable early warnings, minimizing equipment downtime and catastrophic failure.

## ✨ Features

* **Edge ML Inferencing:** Runs lightweight ML models (TensorFlow Lite INT8, Pure C Random Forest) locally on an ESP32.
* **Digital Twin Dashboard:** A real-time Streamlit Python application that acts as a digital twin, simulating edge inference, plotting live telemetry trends, and visualizing model confidence distribution.
* **Data Preprocessing Pipeline:** Extracts key statistical features (RMS Vibration, Kurtosis, Spectral Entropy, Peak Frequency) from raw sensor windowing (1024 samples).
* **Low Latency & Memory Footprint:** Designed to keep feature payloads under 1KB for industrial network transmission.
* **Smart Alerting:** Integrated confidence thresholding (`< 0.75` mapped to "Uncertain") prevents false-positive maintenance triggers.

## 📂 Project Structure

```text
edge-ai-pdm/
├── data/
│   └── processed/
│       └── features.csv            # Extracted datasets for inference
├── models/
│   ├── edge_model.tflite           # Quantized NN for Edge
│   └── random_forest_export.c      # Pure C RF Implementation
├── src/
│   └── demo/
│       ├── app.py                  # Streamlit Digital Twin
│       ├── arduino_esp32.ino       # ESP32 C++ deployment script
│       └── sketch.ino
├── IMPLEMENTATION_LOGS.md          # Full archive of development walkthroughs
├── gemini.md                       # Core system architecture & data schemas
└── run_demo.bat                    # Executable batch file to launch UI
```

## 🚀 How to Run & Evaluate

### 1. Digital Twin Dashboard
Double-click `run_demo.bat` in the root directory. This will automatically launch the Streamlit app in your default web browser. You can fetch simulated telemetry windows and view real-time model predictions and graphs.

### 2. ESP32 Simulation
1. Copy the contents of `src/demo/arduino_esp32.ino`.
2. Navigate to the [Wokwi ESP32 Simulator](https://wokwi.com/projects/new/esp32).
3. Paste the code into `sketch.ino`, ensure your model logic is included, and click **Start** to view the live serial monitor predictions.

## 📝 Changelog & Project Phases

### Phase 1: Data Engineering
* **[Added]** Data schema definition in `gemini.md` (Raw Input, Processed Feature Payload, Model Output).
* **[Added]** Implemented preprocessing to extract RMS, Kurtosis, Spectral Entropy, and Peak Frequency from raw data windows of 1024 samples.

### Phase 2: Model Training & Export
* **[Added]** Trained predictive models for the 4 distinct fault classes.
* **[Added]** Exported Random Forest to pure C array for bare-metal execution.
* **[Added]** Exported TensorFlow model to `edge_model.tflite` utilizing INT8 quantization.

### Phase 3: Deployment & Trigger Logic
* **[Added]** `arduino_esp32.ino` for direct deployment onto ESP32 hardware/Wokwi simulator.
* **[Added]** `app.py` Streamlit dashboard built as a functional Digital Twin.
* **[Added]** Implemented strict thresholding logic (Rule: Confidence < 0.75 triggers "Uncertain" alert) to ensure reliability.
* **[Updated]** Enhanced Streamlit dashboard with real-time Telemetry Trend line charts and Model Confidence Distribution bar charts.

---
*Developed by Kartik Burele | M.Tech in Applied AI and Communications, VNIT*
