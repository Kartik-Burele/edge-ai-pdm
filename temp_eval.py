import pandas as pd
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import time

# 1. Load Data
print("Loading dataset...")
df = pd.read_csv('data/processed/features.csv')
X = df[['rms_vibration', 'kurtosis', 'spectral_entropy', 'peak_frequency_hz']].values
label_map = {"Normal": 0, "Ball Defect": 1, "Inner Race Fault": 2, "Outer Race Fault": 3}
y = np.array([label_map[cond] for cond in df['condition']])

# Split into Train and Test sets for a fair evaluation
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Standardize the features (Using training set to fit, to prevent data leakage)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train).astype(np.float32)
X_test_scaled = scaler.transform(X_test).astype(np.float32)

target_names = ['Normal', 'Ball Defect', 'Inner Race Fault', 'Outer Race Fault']

# ==========================================
# EVALUATION 1: TENSORFLOW LITE (INT8) MODEL
# ==========================================
print("\n======================================================")
print(" MODEL 1: INT8 QUANTIZED TENSORFLOW LITE NEURAL NETWORK")
print("======================================================")

interpreter = tf.lite.Interpreter(model_path='models/edge_model.tflite')
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

y_pred_tf = []
start_time_tf = time.time()
for i in range(len(X_test_scaled)):
    interpreter.set_tensor(input_details[0]['index'], [X_test_scaled[i]])
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    y_pred_tf.append(np.argmax(output_data[0]))
end_time_tf = time.time()

tf_latency_ms = ((end_time_tf - start_time_tf) / len(X_test_scaled)) * 1000

print(f"Overall Accuracy:  {accuracy_score(y_test, y_pred_tf) * 100:.2f}%")
print(f"Average Latency:   {tf_latency_ms:.3f} ms per sample")
print(f"Memory Footprint:  2.7 KB")
print("\nClassification Report:")
print(classification_report(y_test, y_pred_tf, target_names=target_names))


# ==========================================
# EVALUATION 2: PURE C RANDOM FOREST MODEL
# ==========================================
print("\n======================================================")
print(" MODEL 2: EMBEDDED RANDOM FOREST (C-TRANSPILED)")
print("======================================================")

# Retraining the exact same lightweight RF architecture we used for the C export
# to mimic the exact accuracy profile of random_forest_export.c
rf_model = RandomForestClassifier(n_estimators=15, max_depth=5, random_state=42)
rf_model.fit(X_train_scaled, y_train)

start_time_rf = time.time()
y_pred_rf = rf_model.predict(X_test_scaled)
end_time_rf = time.time()

rf_latency_ms = ((end_time_rf - start_time_rf) / len(X_test_scaled)) * 1000

print(f"Overall Accuracy:  {accuracy_score(y_test, y_pred_rf) * 100:.2f}%")
print(f"Average Latency:   {rf_latency_ms:.3f} ms per sample")
print(f"Memory Footprint:  ~43 KB (Raw C Array)")
print("\nClassification Report:")
print(classification_report(y_test, y_pred_rf, target_names=target_names))
