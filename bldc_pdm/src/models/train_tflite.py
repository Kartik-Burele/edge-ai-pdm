import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from sklearn.metrics import classification_report

# Compute paths relative to the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))

PROCESSED_DATA_PATH = os.path.join(WORKSPACE_DIR, "bldc_pdm", "data", "processed", "features.csv")
MODEL_DIR = os.path.join(WORKSPACE_DIR, "bldc_pdm", "models")
TFLITE_MODEL_PATH = os.path.join(MODEL_DIR, "edge_model.tflite")
CC_MODEL_PATH = os.path.join(MODEL_DIR, "model_data.cc")

def train_nn():
    if not os.path.exists(PROCESSED_DATA_PATH):
        print(f"[Error] {PROCESSED_DATA_PATH} not found.")
        return

    os.makedirs(MODEL_DIR, exist_ok=True)
    df = pd.read_csv(PROCESSED_DATA_PATH)
    
    label_map = {
        "Healthy": 0, 
        "Mechanical Damage": 1, 
        "Electrical Damage": 2, 
        "Mech_Elec_Damage": 3
    }
    inverse_map = {v: k for k, v in label_map.items()}
    df['label'] = df['condition'].map(label_map)
    
    feature_cols = [
        "rms_current", 
        "kurtosis_current", 
        "mean_speed", 
        "std_speed", 
        "spectral_entropy_current", 
        "peak_frequency_current"
    ]
    X = df[feature_cols]
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Save the scaler configuration to JSON for the ESP32 or reference
    scaler_params = {
        "mean": scaler.mean_.tolist(),
        "scale": scaler.scale_.tolist(),
        "feature_names": feature_cols
    }
    scaler_path = os.path.join(MODEL_DIR, "scaler_params.json")
    with open(scaler_path, "w") as f:
        json.dump(scaler_params, f, indent=2)
    print(f"Saved scaler parameters to {scaler_path}")
    
    # Build Keras Feedforward Neural Network
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(12, activation='relu', input_shape=(len(feature_cols),)),
        tf.keras.layers.Dense(8, activation='relu'),
        tf.keras.layers.Dense(4, activation='softmax')
    ])
    
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    
    print("Training TFLite Dense Neural Network for BLDC Diagnostics...")
    model.fit(
        X_train_scaled, 
        y_train, 
        epochs=50, 
        batch_size=16, 
        verbose=0, 
        validation_data=(X_test_scaled, y_test)
    )
    
    loss, acc = model.evaluate(X_test_scaled, y_test, verbose=0)
    print(f"[Success] TFLite Validation Accuracy: {acc*100:.2f}%")
    
    # Generate predictions for classification report
    y_pred_probs = model.predict(X_test_scaled)
    y_pred = np.argmax(y_pred_probs, axis=1)
    print(classification_report(y_test, y_pred, target_names=list(label_map.keys())))
    
    # Export to TFLite with Post Training Quantization INT8
    print("Quantizing and exporting to TensorFlow Lite (INT8)...")
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    tflite_model = converter.convert()
    
    with open(TFLITE_MODEL_PATH, 'wb') as f:
        f.write(tflite_model)
    print(f"[Success] Exported TFLite Model to {TFLITE_MODEL_PATH} ({len(tflite_model)} bytes)")
    
    # Write as a C byte array payload for embedded microcontrollers
    hex_array = ', '.join([f'0x{b:02x}' for b in tflite_model])
    with open(CC_MODEL_PATH, 'w') as f:
        f.write("#include <stdint.h>\n")
        f.write(f"const unsigned char edge_model_tflite[] = {{\n{hex_array}\n}};\n")
        f.write(f"const unsigned int edge_model_tflite_len = {len(tflite_model)};\n")
    print(f"[Success] Exported C Array Payload to {CC_MODEL_PATH}")

if __name__ == "__main__":
    train_nn()
