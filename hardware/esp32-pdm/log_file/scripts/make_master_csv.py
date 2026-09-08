import os
import glob
import numpy as np
import pandas as pd
from scipy import signal
 
# ============================================================
# SETTINGS
# ============================================================
 
RAW_FOLDER = "../raw_data"
EXCEL_FILE = "../CC_Load_Data.xlsx"
OUTPUT_FOLDER = "../output"
 
FS = 200                 # ESP32 sampling frequency
WINDOW_SECONDS = 1
WINDOW_SAMPLES = FS * WINDOW_SECONDS
 
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
 
 
# ============================================================
# LOAD MANUAL LOAD DATA
# ============================================================
 
load_df = pd.read_excel(EXCEL_FILE)
 
load_df.columns = [
    "load_A",
    "load_voltage_V",
    "psu_current_A",
    "load_power_W"
]
 
print("\nManual load data:")
print(load_df)
 
 
# ============================================================
# FEATURE FUNCTIONS
# ============================================================
 
def rms(x):
    return np.sqrt(np.mean(x ** 2))
 
 
def peak_to_peak(x):
    return np.max(x) - np.min(x)
 
 
def crest_factor(x):
    r = rms(x)
 
    if r == 0:
        return 0
 
    return np.max(np.abs(x)) / r
 
 
def spectral_features(x, fs):
 
    n = len(x)
 
    # Remove DC component
    x = x - np.mean(x)
 
    # Hann window
    window = np.hanning(n)
 
    x_windowed = x * window
 
    # FFT
    spectrum = np.fft.rfft(x_windowed)
 
    magnitude = np.abs(spectrum)
 
    frequencies = np.fft.rfftfreq(n, d=1/fs)
 
    # Ignore DC
    magnitude[0] = 0
 
    dominant_index = np.argmax(magnitude)
 
    dominant_frequency = frequencies[dominant_index]
 
    dominant_amplitude = magnitude[dominant_index]
 
    spectral_energy = np.sum(magnitude ** 2)
 
    if np.sum(magnitude) > 0:
        spectral_centroid = np.sum(
            frequencies * magnitude
        ) / np.sum(magnitude)
    else:
        spectral_centroid = 0
 
    return (
        dominant_frequency,
        dominant_amplitude,
        spectral_energy,
        spectral_centroid
    )
 
 
# ============================================================
# PROCESS ONE CSV
# ============================================================
 
def process_file(file_path, load_row):
 
    filename = os.path.basename(file_path)
 
    print("\nProcessing:", filename)
 
    df = pd.read_csv(file_path)
 
    required_columns = [
        "timestamp_ms",
        "ax",
        "ay",
        "az",
        "acs_adc"
    ]
 
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(
                f"{filename}: Missing column {column}"
            )
 
    # --------------------------------------------------------
    # Check timestamps
    # --------------------------------------------------------
 
    timestamps = df["timestamp_ms"].values
 
    dt = np.diff(timestamps)
 
    median_dt = np.median(dt)
 
    estimated_fs = 1000.0 / median_dt
 
    print(
        f"Samples = {len(df)}, "
        f"Duration = {(timestamps[-1]-timestamps[0])/1000:.3f}s, "
        f"Estimated Fs = {estimated_fs:.2f} Hz"
    )
 
    # --------------------------------------------------------
    # Use only complete 1-second windows
    # --------------------------------------------------------
 
    number_of_windows = len(df) // WINDOW_SAMPLES
 
    results = []
 
    for window_number in range(number_of_windows):
 
        start = window_number * WINDOW_SAMPLES
 
        end = start + WINDOW_SAMPLES
 
        w = df.iloc[start:end].copy()
 
        ax = w["ax"].to_numpy()
        ay = w["ay"].to_numpy()
        az = w["az"].to_numpy()
 
        acs = w["acs_adc"].to_numpy()
 
        # ----------------------------------------------------
        # Remove mean from each acceleration axis
        # This removes the static/DC component including
        # gravity for this window.
        # ----------------------------------------------------
 
        ax_dynamic = ax - np.mean(ax)
        ay_dynamic = ay - np.mean(ay)
        az_dynamic = az - np.mean(az)
 
        # ----------------------------------------------------
        # Acceleration magnitude
        # ----------------------------------------------------
 
        magnitude = np.sqrt(
            ax_dynamic**2 +
            ay_dynamic**2 +
            az_dynamic**2
        )
 
        # ----------------------------------------------------
        # Time-domain features
        # ----------------------------------------------------
 
        row = {
 
            "file": filename,
 
            "window": window_number,
 
            "start_time_s":
                (w["timestamp_ms"].iloc[0]
                 - df["timestamp_ms"].iloc[0]) / 1000,
 
            # Operating condition
            "load_A": load_row["load_A"],
            "load_voltage_V":
                load_row["load_voltage_V"],
            "psu_current_A":
                load_row["psu_current_A"],
            "load_power_W":
                load_row["load_power_W"],
 
            # AX
            "ax_mean": np.mean(ax),
            "ax_std": np.std(ax_dynamic),
            "ax_rms": rms(ax_dynamic),
            "ax_peak": np.max(np.abs(ax_dynamic)),
            "ax_p2p": peak_to_peak(ax_dynamic),
            "ax_crest": crest_factor(ax_dynamic),
 
            # AY
            "ay_mean": np.mean(ay),
            "ay_std": np.std(ay_dynamic),
            "ay_rms": rms(ay_dynamic),
            "ay_peak": np.max(np.abs(ay_dynamic)),
            "ay_p2p": peak_to_peak(ay_dynamic),
            "ay_crest": crest_factor(ay_dynamic),
 
            # AZ
            "az_mean": np.mean(az),
            "az_std": np.std(az_dynamic),
            "az_rms": rms(az_dynamic),
            "az_peak": np.max(np.abs(az_dynamic)),
            "az_p2p": peak_to_peak(az_dynamic),
            "az_crest": crest_factor(az_dynamic),
 
            # Magnitude
            "acc_mag_rms": rms(magnitude),
            "acc_mag_std": np.std(magnitude),
            "acc_mag_peak": np.max(np.abs(magnitude)),
            "acc_mag_p2p": peak_to_peak(magnitude),
 
            # ACS712
            "acs_mean": np.mean(acs),
            "acs_std": np.std(acs),
            "acs_rms": rms(acs),
            "acs_min": np.min(acs),
            "acs_max": np.max(acs),
            "acs_p2p": peak_to_peak(acs),
        }
 
        # ----------------------------------------------------
        # FFT features using acceleration magnitude
        # ----------------------------------------------------
 
        (
            dominant_frequency,
            dominant_amplitude,
            spectral_energy,
            spectral_centroid
        ) = spectral_features(magnitude, FS)
 
        row["dominant_frequency_Hz"] = dominant_frequency
        row["dominant_amplitude"] = dominant_amplitude
        row["spectral_energy"] = spectral_energy
        row["spectral_centroid_Hz"] = spectral_centroid
 
        results.append(row)
 
    return results
 
 
# ============================================================
# PROCESS ALL CSV FILES
# ============================================================
 
csv_files = sorted(
    glob.glob(
        os.path.join(
            RAW_FOLDER,
            "healthy_cc_*.csv"
        )
    )
)
 
all_results = []
 
print("\nFound", len(csv_files), "CSV files.")
 
if len(csv_files) == 0:
    raise RuntimeError(
        "No healthy_cc_*.csv files found."
    )
 
 
for file_path in csv_files:
 
    filename = os.path.basename(file_path)
 
    # --------------------------------------------------------
    # Extract load value from filename
    # healthy_cc_01A -> 0.1 A
    # healthy_cc_10A -> 1.0 A
    # --------------------------------------------------------
 
    number = filename.split("_")[-1].replace("A.csv", "")
 
    load_value = int(number) / 10.0
 
    # Find matching row in Excel
    matches = load_df[
        np.isclose(
            load_df["load_A"],
            load_value
        )
    ]
 
    if len(matches) != 1:
        raise ValueError(
            f"No unique Excel entry for {load_value} A"
        )
 
    load_row = matches.iloc[0]
 
    results = process_file(
        file_path,
        load_row
    )
 
    all_results.extend(results)
 
 
# ============================================================
# SAVE FEATURE DATASET
# ============================================================
 
features_df = pd.DataFrame(all_results)
 
output_file = os.path.join(
    OUTPUT_FOLDER,
    "healthy_features.csv"
)
 
features_df.to_csv(
    output_file,
    index=False
)
 
print("\n========================================")
print("PROCESSING COMPLETE")
print("========================================")
 
print(
    "Total feature windows:",
    len(features_df)
)
 
print(
    "Output:",
    output_file
)
 
print("\nFirst rows:")
print(features_df.head())
 