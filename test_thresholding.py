import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import pandas as pd

print("======================================================")
print(" SMART ALERTING RULE TEST (75% THRESHOLD)")
print("======================================================\n")

# 1. Load the exact model used in Edge App
interpreter = tf.lite.Interpreter(model_path='models/edge_model.tflite')
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

target_labels = {0: "Normal", 1: "Ball Defect", 2: "Inner Race Fault", 3: "Outer Race Fault"}

# 2. We need the scaler to correctly scale our artificial inputs
df = pd.read_csv('data/processed/features.csv')
X = df[['rms_vibration', 'kurtosis', 'spectral_entropy', 'peak_frequency_hz']].values
scaler = StandardScaler()
scaler.fit(X)

def simulate_inference(features_array, scenario_name):
    # Scale exactly like the live app
    scaled_input = scaler.transform([features_array]).astype(np.float32)
    
    # Run TFLite inference
    interpreter.set_tensor(input_details[0]['index'], scaled_input)
    interpreter.invoke()
    probabilities = interpreter.get_tensor(output_details[0]['index'])[0]
    
    # Extract prediction
    pred_class_idx = int(np.argmax(probabilities))
    confidence = float(probabilities[pred_class_idx])
    
    print(f"--- SCENARIO: {scenario_name} ---")
    print(f"Raw Probabilities: [Normal: {probabilities[0]:.2f}, Ball: {probabilities[1]:.2f}, Inner: {probabilities[2]:.2f}, Outer: {probabilities[3]:.2f}]")
    print(f"Top Class: {target_labels[pred_class_idx]} (Confidence: {confidence*100:.1f}%)")
    
    # APPLY THE 75% BUSINESS LOGIC RULE
    if confidence < 0.75:
        print(">> SYSTEM DECISION: [UNCERTAIN] - Confidence below 75%. Suppressing factory alarm.")
    else:
        if target_labels[pred_class_idx] == "Normal":
            print(">> SYSTEM DECISION: [NOMINAL] - Motor is healthy.")
        else:
            print(f">> SYSTEM DECISION: [CRITICAL ALARM] - {target_labels[pred_class_idx]} detected! Shutting down motor.")
    print()

# Test 1: Highly confident Normal (Clear signal)
# Taking an actual normal sample
normal_sample = X[df['condition'] == 'Normal'][0]
simulate_inference(normal_sample, "Clear Healthy Motor Reading")

# Test 2: Highly confident Fault (Clear signal)
# Taking an actual inner race fault sample
fault_sample = X[df['condition'] == 'Inner Race Fault'][0]
simulate_inference(fault_sample, "Clear Bearing Fault Reading")

# Test 3: Noisy/Ambiguous Signal (Artificial)
# To find a truly uncertain sample, we interpolate exactly between Normal and Fault 
# to find the model's decision boundary where confidence drops.
print("--- SCENARIO: Noisy/Ambiguous Sensor Reading ---")
for alpha in np.linspace(0, 1, 100):
    ambiguous_sample = alpha * normal_sample + (1 - alpha) * fault_sample
    scaled_input = scaler.transform([ambiguous_sample]).astype(np.float32)
    interpreter.set_tensor(input_details[0]['index'], scaled_input)
    interpreter.invoke()
    probs = interpreter.get_tensor(output_details[0]['index'])[0]
    if np.max(probs) < 0.75:
        pred_class_idx = int(np.argmax(probs))
        confidence = float(probs[pred_class_idx])
        print(f"Found Boundary Sample at interpolation alpha={alpha:.2f}")
        print(f"Raw Probabilities: [Normal: {probs[0]:.2f}, Ball: {probs[1]:.2f}, Inner: {probs[2]:.2f}, Outer: {probs[3]:.2f}]")
        print(f"Top Class: {target_labels[pred_class_idx]} (Confidence: {confidence*100:.1f}%)")
        print(">> SYSTEM DECISION: [UNCERTAIN] - Confidence below 75%. Suppressing factory alarm.\n")
        break
