# Project Implementation Plans and Walkthroughs Log

This document serves as a consolidated record of all implementation plans and walkthroughs generated during the development of the Edge AI Predictive Maintenance project.

---

## Phase 1: Data Engineering & Preprocessing

### Implementation Plan
* **Objective:** Define data schemas for raw vibration and temperature sensor data to ensure compatibility between the Sensors Layer and the Machine Learning Model.
* **Proposed Changes:** 
  * Create `gemini.md` to establish project laws regarding data shapes (Raw Input, Processed Features, Model Output).
  * Enforce behavioral rules: strict 1024 sample windowing, and keeping processed payloads under 1KB.
  * Extract specific features: RMS, Kurtosis, Spectral Entropy, and Peak Frequency.

### Walkthrough
* Generated `data/processed/features.csv` representing simulated telemetry across 4 target motor states: Normal, Ball Defect, Inner Race Fault, Outer Race Fault.
* Data pipeline strictly adheres to the schema and successfully distills raw high-frequency waveforms into lightweight statistical features.

---

## Phase 2: Model Training & Export

### Implementation Plan
* **Objective:** Train lightweight machine learning models suitable for resource-constrained edge devices (ESP32).
* **Proposed Changes:** 
  * Train and compare algorithms (Decision Trees/Random Forests vs. small Neural Networks).
  * Quantize the Neural Network to INT8 and export as `.tflite`.
  * Transpile the Random Forest model directly into a pure C array.

### Walkthrough
* Trained models achieving high accuracy on the 4 fault classes.
* Successfully exported `models/edge_model.tflite`.
* Exported the C-compatible Random Forest scoring logic (`random_forest_export.c`) for bare-metal microcontroller environments.

---

## Phase 3: Edge Deployment Deliverables & Trigger

### Implementation Plan
* **Objective:** Complete the deployment logic for both physical microcontrollers and a visual digital twin simulator.
* **Proposed Changes:**
  * **Option A:** Write an Arduino C++ script (`src/demo/arduino_esp32.ino`) designed for the Wokwi ESP32 simulator, incorporating the pure C `score()` function.
  * **Option B:** Build a Streamlit web application (`src/demo/app.py`) to run the TensorFlow Lite quantization in Python, simulating the exact same edge logic with a rich dark-mode UI.
  * Enforce the business logic rule: `< 0.75` confidence must return an "Uncertain" state.

### Walkthrough
* Created `arduino_esp32.ino` complete with dummy payload looping and serial monitor alerts.
* Created `app.py` Digital Twin using `Streamlit`.
* Created `run_demo.bat` to allow zero-friction launching of the dashboard for evaluation.

---

## Phase 4: UI Enhancements & Visualization

### Implementation Plan
* **Objective:** Improve the Streamlit Digital Twin by adding time-series graphing capabilities to visualize the continuous telemetry stream.
* **Proposed Changes:**
  * Add session state tracking to record the last 50 telemetry windows.
  * Render a line chart for Telemetry Trends.
  * Render a bar chart for Confidence Distribution across the 4 possible fault states.

### Walkthrough
* Enhanced `app.py` with `st.line_chart` for historical `RMS Vibration` and `Entropy` tracking.
* Enhanced `app.py` with `st.bar_chart` utilizing the exact softmax probability outputs from the TFLite model.
* System is now visually complete and ready for the M.Tech evaluation presentation.
