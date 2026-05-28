import os
import json
import numpy as np
import pandas as pd
from scipy.stats import kurtosis, entropy

# Compute absolute paths relative to the script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))

RAW_INPUT_DIR = os.path.join(WORKSPACE_DIR, "DUDU-BLDC", "DUDU-BLDC", "Data", "InputData")
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "bldc_pdm", "data", "processed")
WINDOW_SIZE = 1024
FS = 5000  # Our downsampled frequency is 5 kHz (raw 50 kHz downsampled by 10)

def compute_features(window_current, window_roto, fs=5000):
    # Convert from Voltage to engineering units
    current_a = (window_current - 2.5) * 20.0 / 2.5
    speed_rpm = window_roto * 10000.0

    # RMS Current
    rms_curr = np.sqrt(np.mean(current_a**2))
    
    # Kurtosis Current
    kurt_curr = kurtosis(current_a, fisher=False)
    
    # Speed statistics
    mean_spd = np.mean(speed_rpm)
    std_spd = np.std(speed_rpm)
    
    # Spectral features on Current
    fft_vals = np.abs(np.fft.rfft(current_a))
    freqs = np.fft.rfftfreq(len(current_a), 1.0/fs)
    
    peak_freq = freqs[np.argmax(fft_vals)]
    
    power_spectrum = fft_vals ** 2
    if np.sum(power_spectrum) > 0:
        psd_norm = power_spectrum / np.sum(power_spectrum)
        spec_entropy = entropy(psd_norm)
    else:
        spec_entropy = 0.0
        
    return {
        "rms_current": float(rms_curr),
        "kurtosis_current": float(kurt_curr),
        "mean_speed": float(mean_spd),
        "std_speed": float(std_spd),
        "spectral_entropy_current": float(spec_entropy),
        "peak_frequency_current": float(peak_freq)
    }

def process_bldc():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_features = []
    
    # Mapping raw CSV files to conditions and labels
    file_mappings = {
        "healthy_1.csv": ("Healthy", "None"),
        "healthy_2.csv": ("Healthy", "None"),
        "healthy_zip_1.csv": ("Mechanical Damage", "Ziptie"),
        "healthy_zip_2.csv": ("Mechanical Damage", "Ziptie"),
        "faulty_1.csv": ("Electrical Damage", "Electrical"),
        "faulty_2.csv": ("Electrical Damage", "Electrical"),
        "faulty_zip_1.csv": ("Mech_Elec_Damage", "Ziptie & Electrical"),
        "faulty_zip_2.csv": ("Mech_Elec_Damage", "Ziptie & Electrical")
    }
    
    example_json_saved = False

    for file_name, (condition, fault_type) in file_mappings.items():
        file_path = os.path.join(RAW_INPUT_DIR, file_name)
        if not os.path.exists(file_path):
            print(f"[Warning] Missing raw data file {file_path}. Skipping.")
            continue
        
        print(f"Loading raw file {file_path} ...")
        # Load raw file (skip 6 header rows, semicolon delimited)
        df = pd.read_csv(file_path, delimiter=";", skiprows=6)
        
        # Ensure we have the correct columns
        if 'CURRENT (V)' not in df.columns or 'ROTO (V)' not in df.columns:
            print(f"[Error] Required columns 'CURRENT (V)' or 'ROTO (V)' not found in {file_name}.")
            continue
        
        # Downsample by 10 (taking every 10th sample) to get 5 kHz sampling rate
        df_down = df.iloc[::10].copy()
        
        current_signal = df_down['CURRENT (V)'].values
        roto_signal = df_down['ROTO (V)'].values
        
        num_windows = len(df_down) // WINDOW_SIZE
        print(f"Extracting {num_windows} windows of size {WINDOW_SIZE} from downsampled {file_name}")
        
        for w in range(num_windows):
            w_start = w * WINDOW_SIZE
            w_end = w_start + WINDOW_SIZE
            
            win_curr = current_signal[w_start:w_end]
            win_roto = roto_signal[w_start:w_end]
            
            feats = compute_features(win_curr, win_roto, fs=FS)
            feats["motor_id"] = "MOTOR_BLDC_001"
            feats["condition"] = condition
            feats["fault_type"] = fault_type
            
            all_features.append(feats)
            
            # Save the very first one as an example to prove the Edge Invariant (<1KB)
            if not example_json_saved:
                sample_payload = {
                    "motor_id": feats["motor_id"],
                    "features": {k: feats[k] for k in feats if k not in ["motor_id", "condition", "fault_type"]}
                }
                with open(os.path.join(OUTPUT_DIR, "features.json"), "w") as f:
                    json.dump(sample_payload, f, indent=2)
                example_json_saved = True

    if not all_features:
        print("[Error] No features extracted!")
        return

    df_out = pd.DataFrame(all_features)
    out_csv = os.path.join(OUTPUT_DIR, "features.csv")
    df_out.to_csv(out_csv, index=False)
    print(f"[Success] Processed {len(all_features)} windows. Saved to {out_csv}")

if __name__ == "__main__":
    process_bldc()
