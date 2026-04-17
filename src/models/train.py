import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import m2cgen as m2c

PROCESSED_DATA_PATH = "data/processed/features.csv"
MODEL_DIR = "models"

def train_model():
    if not os.path.exists(PROCESSED_DATA_PATH):
        print(f"❌ Error: {PROCESSED_DATA_PATH} not found. Run preprocess.py first.")
        return

    os.makedirs(MODEL_DIR, exist_ok=True)
    df = pd.DataFrame(pd.read_csv(PROCESSED_DATA_PATH))
    
    feature_cols = ["rms_vibration", "kurtosis", "spectral_entropy", "peak_frequency_hz"]
    X = df[feature_cols]
    y = df["condition"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Random Forest Baseline Model...")
    clf = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Validation Accuracy: {acc*100:.2f}%")
    print(classification_report(y_test, y_pred))
    
    # Test Behavioral Rule Threshold: Low confidence (< 0.75)
    idx = 0
    confidence = max(y_prob[idx])
    pred_label = y_pred[idx]
    
    if confidence < 0.75:
        print(f"Flagged low confidence ({confidence:.2f}) rule. Changing prediction from '{pred_label}' to 'Uncertain'")
        pred_label = "Uncertain"
        
    print(f"Sample Inference -> Predicted: {pred_label} (Confidence: {confidence:.2f})")
    
    # Placeholder for model export
    print("Model logic finalized. Exporting to direct C code via m2cgen...")
    
    code = m2c.export_to_c(clf)
    rf_export_path = os.path.join(MODEL_DIR, "random_forest_export.c")
    with open(rf_export_path, "w") as f:
        f.write(code)
    print(f"Exported pure C random forest to {rf_export_path} (Size: {len(code)} bytes)")

if __name__ == "__main__":
    train_model()
