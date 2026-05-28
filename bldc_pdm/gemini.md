# Data Schema & Maintenance Log (gemini.md) - BLDC Motor Project

*This file is LAW. Code only starts after the Payload shape is confirmed here.*

1. Data-First Rule: JSON Schema Definition
To ensure compatibility between the Sensors Layer and the Machine Learning Model, we define the following data shapes for the BLDC motor diagnostic system.

## Input Payload Shape
A. Raw Input Payload (input_bldc.json)
This represents a single "window" of data captured from the sensors (current sensor and optical encoder/rotational speed sensor) before it undergoes Signal Processing.
```json
{
  "motor_id": "MOTOR_BLDC_001",
  "timestamp": "2026-05-23T22:30:00Z",
  "sampling_rate_hz": 5000,
  "window_size": 1024,
  "sensors": {
    "current_v": [2.49, 2.48, 2.50, "..."], 
    "roto_v": [-0.0004, -0.0004, -0.0003, "..."]
  }
}
```
* current_v: Array of exactly 1024 floats representing raw voltage from current sensor.
* roto_v: Array of exactly 1024 floats representing raw voltage from rotor speed sensor.

B. Processed Feature Payload (features.json)
This is the output of the preprocess.py script after Signal Conversion, Windowing, FFT Analysis, and Feature Extraction.
```json
{
  "motor_id": "MOTOR_BLDC_001",
  "features": {
    "rms_current": 1.25,
    "kurtosis_current": 3.01,
    "mean_speed": 1845.2,
    "std_speed": 4.5,
    "spectral_entropy_current": 0.82,
    "peak_frequency_current": 150.0
  }
}
```
* Features Included: RMS, Kurtosis, and Spectral Entropy of current, and statistical summaries of speed.

## Output Payload Shape
C. Model Output Payload (classification.json)
The final inference result delivered by the Embedded Edge Device.

```json
{
  "motor_id": "MOTOR_BLDC_001",
  "timestamp": "2026-05-23T22:30:05Z",
  "prediction": {
    "condition": "Electrical Damage",
    "confidence_score": 0.942,
    "fault_type": "Electrical"
  },
  "alert_level": "CRITICAL",
  "recommendation": "Inspect stator windings and current inputs immediately"
}
```
* Condition: Classified into Healthy, Mechanical Damage, Electrical Damage, or Mech_Elec_Damage.
* Recommendation: Precautionary actions to prevent stator burnout or rotor misalignment.

2. Behavioral Rules (A.N.T. Layer 1)
* Windowing: The preprocess.py tool must only accept arrays of exactly 1024 samples to ensure FFT consistency and edge constraint alignment.

* Thresholding: Any confidence_score below 0.75 must be flagged as "Uncertain" to prevent false maintenance triggers.

* Edge Invariant: The features.json size must be kept under 1KB to ensure low-latency transmission over industrial networks.

## Maintenance Log
- 2026-05-23: Initial release of BLDC motor schema and rules.
