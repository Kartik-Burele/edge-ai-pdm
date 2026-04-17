import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from sklearn.metrics import classification_report

PROCESSED_DATA_PATH = "data/processed/features.csv"
MODEL_DIR = "models"
TFLITE_MODEL_PATH = os.path.join(MODEL_DIR, "edge_model.tflite")
CC_MODEL_PATH = os.path.join(MODEL_DIR, "model_data.cc")

def train_nn():
    if not os.path.exists(PROCESSED_DATA_PATH):
        print(f"❌ Error: {PROCESSED_DATA_PATH} not found.")
        return

    os.makedirs(MODEL_DIR, exist_ok=True)
    df = pd.read_csv(PROCESSED_DATA_PATH)
    
    label_map = {"Normal": 0, "Ball Defect": 1, "Inner Race Fault": 2, "Outer Race Fault": 3}
    inverse_map = {v:k for k,v in label_map.items()}
    df['label'] = df['condition'].map(label_map)
    
    feature_cols = ["rms_vibration", "kurtosis", "spectral_entropy", "peak_frequency_hz"]
    X = df[feature_cols]
    y = df['label']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(8, activation='relu', input_shape=(len(feature_cols),)),
        tf.keras.layers.Dense(8, activation='relu'),
        tf.keras.layers.Dense(4, activation='softmax')
    ])
    
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    
    print("Training TFLite Dense Neural Network...")
    model.fit(X_train_scaled, y_train, epochs=30, batch_size=16, verbose=0, validation_data=(X_test_scaled, y_test))
    
    loss, acc = model.evaluate(X_test_scaled, y_test, verbose=0)
    print(f"TFLite Validation Accuracy: {acc*100:.2f}%")
    
    # Export TFLite with Post Training Quantization INT8
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    tflite_model = converter.convert()
    
    with open(TFLITE_MODEL_PATH, 'wb') as f:
        f.write(tflite_model)
    
    print(f"Exported TFLite Model (Size: {len(tflite_model)} bytes)")
    
    hex_array = ', '.join([f'0x{b:02x}' for b in tflite_model])
    with open(CC_MODEL_PATH, 'w') as f:
        f.write("#include <stdint.h>\n")
        f.write(f"const unsigned char edge_model_tflite[] = {{\n{hex_array}\n}};\n")
        f.write(f"const unsigned int edge_model_tflite_len = {len(tflite_model)};\n")
    print(f"Exported C Array Payload to {CC_MODEL_PATH}")

if __name__ == "__main__":
    train_nn()
