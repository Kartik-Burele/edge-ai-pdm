# Data Schema & Maintenance Log (gemini.md)

*This file is LAW. Code only starts after the Payload shape is confirmed here.*

1. Data-First Rule: JSON Schema Definition
To ensure compatibility between the Sensors Layer and the Machine Learning Model, we define the following data shapes.

## Input Payload Shape
A. Raw Input Payload (input_vibration.json)
This represents a single "window" of data captured from the sensors (e.g., ADXL345 and DS18B20) before it undergoes Signal Processing.
```json
{
  "motor_id": "MOTOR_DE_001",
  "timestamp": "2026-04-15T22:30:00Z",
  "sampling_rate_hz": 12000,
  "window_size": 1024,
  "sensors": {
    "vibration_x": [0.012, -0.005, 0.089, "..."], 
    "temperature_c": 42.5
  }
}
```
* vibration_x: Array of 1024 floats representing raw acceleration.
* temperature_c: Real-time reading to detect thermal anomalies.

B. Processed Feature Payload (features.json)
This is the output of the preprocess.py script after FFT Analysis and Feature Extraction. This is what the ML model actually "sees."
```json
{
  "motor_id": "MOTOR_DE_001",
  "features": {
    "rms_vibration": 0.045,
    "kurtosis": 3.2,
    "spectral_entropy": 0.88,
    "peak_frequency_hz": 142.5
  }
}
```
* Features Included: RMS, Kurtosis, and Spectral Entropy as per project roadmap.

## Output Payload Shape
C. Model Output Payload (classification.json)
The final inference result delivered by the Embedded Edge Device.

```json
{
  "motor_id": "MOTOR_DE_001",
  "timestamp": "2026-04-15T22:30:05Z",
  "prediction": {
    "condition": "Bearing Fault",
    "confidence_score": 0.962,
    "fault_type": "Inner Race"
  },
  "alert_level": "CRITICAL",
  "recommendation": "Inspect drive-end bearing immediately"
}
```
* Condition: Classified into Normal, Imbalance, Misalignment, or Bearing Fault .
* Recommendation: Early warning to reduce equipment downtime.

2. Behavioral Rules (A.N.T. Layer 1)
* Windowing: The preprocess.py tool must only accept arrays of exactly 1024 samples to ensure FFT consistency.

* Thresholding: Any confidence_score below 0.75 must be flagged as "Uncertain" to prevent false maintenance triggers.

* Edge Invariant: The features.json size must be kept under 1KB to ensure low-latency transmission over industrial networks.

## Maintenance Log
- 

