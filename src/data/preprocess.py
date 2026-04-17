import os
import json
import scipy.io
import numpy as np
import pandas as pd
from scipy.stats import kurtosis, entropy

RAW_DATA_PATH = "data/raw/cwru"
OUTPUT_DIR = "data/processed"
WINDOW_SIZE = 1024

def compute_features(window, fs=12000):
    # RMS
    rms = np.sqrt(np.mean(window**2))
    # Kurtosis
    kurt = kurtosis(window, fisher=False)
    # Spectral Entropy and Peak Freq
    fft_vals = np.abs(np.fft.rfft(window))
    freqs = np.fft.rfftfreq(len(window), 1/fs)
    
    # Peak frequency
    peak_freq = freqs[np.argmax(fft_vals)]
    
    # Spectral Entropy
    power_spectrum = fft_vals ** 2
    psd_norm = power_spectrum / np.sum(power_spectrum)
    spec_entropy = entropy(psd_norm)
    
    return {
        "rms_vibration": float(rms),
        "kurtosis": float(kurt),
        "spectral_entropy": float(spec_entropy),
        "peak_frequency_hz": float(peak_freq)
    }

def process_cwru():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_features = []
    
    files = [f for f in os.listdir(RAW_DATA_PATH) if f.endswith('.mat')]
    conditions = {
        "b007": "Ball Defect",
        "ir": "Inner Race Fault",
        "or007": "Outer Race Fault",
        "nbd": "Normal"
    }    
    example_json_saved = False

    for file_name in files:
        file_path = os.path.join(RAW_DATA_PATH, file_name)
        if not os.path.exists(file_path):
            print(f"Skipping {file_name}, missing.")
            continue
            
        mat_data = scipy.io.loadmat(file_path)
        data_keys = [k for k in mat_data.keys() if 'DE_time' in k]
        if not data_keys:
            continue
        
        signal = mat_data[data_keys[0]].flatten()
        prefix = file_name.split('_')[0]
        condition = conditions.get(prefix, "Normal")
        
        num_windows = len(signal) // WINDOW_SIZE
        
        for w in range(num_windows):
            window = signal[w * WINDOW_SIZE : (w + 1) * WINDOW_SIZE]
            feats = compute_features(window)
            feats["motor_id"] = "MOTOR_DE_001"
            feats["condition"] = condition
            feats["fault_type"] = prefix if condition == "Bearing Fault" else "None"
            
            all_features.append(feats)
            
            # Save the very first one as an example to prove the Edge Invariant (<1KB)
            if not example_json_saved:
                with open(os.path.join(OUTPUT_DIR, "features.json"), "w") as f:
                    json.dump({"motor_id": feats["motor_id"], "features": {k: feats[k] for k in feats if k not in ["motor_id", "condition", "fault_type"]}}, f, indent=2)
                example_json_saved = True

    df = pd.DataFrame(all_features)
    df.to_csv(os.path.join(OUTPUT_DIR, "features.csv"), index=False)
    print(f"Processed {len(all_features)} windows of size 1024.")

if __name__ == "__main__":
    process_cwru()
