import os
import glob
import re
import numpy as np
import pandas as pd

# ============================================================
# SETTINGS
# ============================================================

RAW_FOLDER = r'C:\Users\40036626\Documents\Kartik\Code_v1\PDM_V1\log_file\29_08_26'
EXCEL_FILE = r'C:\Users\40036626\Documents\Kartik\Code_v1\PDM_V1\log_file\CC_Load_Data.xlsx' 
OUTPUT_FOLDER = r'C:\Users\40036626\Documents\Kartik\Code_v1\PDM_V1\log_file\output290826'

FS = 200
WINDOW_SECONDS = 1
WINDOW_SAMPLES = FS * WINDOW_SECONDS

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ============================================================
# LOAD MANUAL LOAD DATA
# ============================================================

load_df = pd.read_excel(EXCEL_FILE)

print("\nManual load data:")
print(load_df)


# ============================================================
# NORMALIZE MANUAL EXCEL DATA
# ============================================================

# Expected final format:
#
# load_A
# load_voltage_V
# psu_current_A
# load_power_W
# supply_voltage_V
#
# If your Excel currently has 3 separate blocks
# (Iteration-1 / Iteration-2 / Iteration-3), see note below.
# ============================================================


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

    # Remove DC
    x = x - np.mean(x)

    # Hann window
    window = np.hanning(n)

    x_windowed = x * window

    # FFT
    spectrum = np.fft.rfft(x_windowed)

    magnitude = np.abs(spectrum)

    frequencies = np.fft.rfftfreq(
        n,
        d=1 / fs
    )

    # Ignore DC
    magnitude[0] = 0

    dominant_index = np.argmax(magnitude)

    dominant_frequency = frequencies[dominant_index]

    dominant_amplitude = magnitude[dominant_index]

    spectral_energy = np.sum(magnitude ** 2)

    if np.sum(magnitude) > 0:

        spectral_centroid = (
            np.sum(frequencies * magnitude)
            / np.sum(magnitude)
        )

    else:

        spectral_centroid = 0

    return (
        dominant_frequency,
        dominant_amplitude,
        spectral_energy,
        spectral_centroid
    )


# ============================================================
# RPM FEATURES
# ============================================================

def rpm_features(rpm):

    rpm = np.asarray(rpm, dtype=float)

    # Valid encoder readings
    valid = rpm > 0

    valid_rpm = rpm[valid]

    total_samples = len(rpm)

    valid_samples = len(valid_rpm)

    if valid_samples == 0:

        return {
            "rpm_mean": 0,
            "rpm_median": 0,
            "rpm_std": 0,
            "rpm_min": 0,
            "rpm_max": 0,
            "rpm_p2p": 0,
            "rpm_cv_percent": 0,
            "rpm_valid_fraction": 0,
            "rpm_zero_fraction": 1
        }

    rpm_mean = np.mean(valid_rpm)

    rpm_std = np.std(valid_rpm)

    if rpm_mean > 0:

        rpm_cv = (
            rpm_std / rpm_mean
        ) * 100

    else:

        rpm_cv = 0

    return {

        "rpm_mean": rpm_mean,

        "rpm_median":
            np.median(valid_rpm),

        "rpm_std":
            rpm_std,

        "rpm_min":
            np.min(valid_rpm),

        "rpm_max":
            np.max(valid_rpm),

        "rpm_p2p":
            np.max(valid_rpm)
            - np.min(valid_rpm),

        "rpm_cv_percent":
            rpm_cv,

        "rpm_valid_fraction":
            valid_samples / total_samples,

        "rpm_zero_fraction":
            np.sum(~valid) / total_samples
    }


# ============================================================
# EXTRACT LOAD + ITERATION FROM FILENAME
# ============================================================

def parse_filename(filename):

    """
    Expected:

        healthy_cc_01A_1.csv
        healthy_cc_01A_2.csv
        healthy_cc_01A_3.csv

        healthy_cc_10A_1.csv
        healthy_cc_20A_3.csv

    Returns:

        load_value
        iteration
    """

    pattern = r"healthy_cc_(\d+)A_(\d+)\.csv"

    match = re.match(pattern, filename)

    if not match:

        raise ValueError(
            f"Unexpected filename format: {filename}"
        )

    load_number = int(match.group(1))

    iteration = int(match.group(2))

    load_value = load_number / 10.0

    return load_value, iteration


# ============================================================
# PROCESS ONE CSV
# ============================================================

def process_file(
    file_path,
    load_row,
    iteration
):

    filename = os.path.basename(file_path)

    print("\nProcessing:", filename)

    df = pd.read_csv(file_path)

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    required_columns = [
        "timestamp_ms",
        "ax",
        "ay",
        "az",
        "acs_adc",
        "rpm"
    ]

    for column in required_columns:

        if column not in df.columns:

            raise ValueError(
                f"{filename}: Missing column {column}"
            )

    # --------------------------------------------------------
    # Timestamp check
    # --------------------------------------------------------

    timestamps = df["timestamp_ms"].values

    dt = np.diff(timestamps)

    median_dt = np.median(dt)

    estimated_fs = 1000.0 / median_dt

    duration = (
        timestamps[-1]
        - timestamps[0]
    ) / 1000.0

    print(
        f"Samples = {len(df)}, "
        f"Duration = {duration:.3f}s, "
        f"Estimated Fs = {estimated_fs:.2f} Hz"
    )

    # --------------------------------------------------------
    # Number of complete windows
    # --------------------------------------------------------

    number_of_windows = (
        len(df) // WINDOW_SAMPLES
    )

    results = []

    for window_number in range(
        number_of_windows
    ):

        start = (
            window_number
            * WINDOW_SAMPLES
        )

        end = (
            start
            + WINDOW_SAMPLES
        )

        w = df.iloc[start:end].copy()

        # ----------------------------------------------------
        # Raw signals
        # ----------------------------------------------------

        ax = w["ax"].to_numpy()

        ay = w["ay"].to_numpy()

        az = w["az"].to_numpy()

        acs = w["acs_adc"].to_numpy()

        rpm = w["rpm"].to_numpy()

        # ----------------------------------------------------
        # Remove acceleration DC component
        # ----------------------------------------------------

        ax_dynamic = (
            ax - np.mean(ax)
        )

        ay_dynamic = (
            ay - np.mean(ay)
        )

        az_dynamic = (
            az - np.mean(az)
        )

        # ----------------------------------------------------
        # Acceleration magnitude
        # ----------------------------------------------------

        magnitude = np.sqrt(
            ax_dynamic ** 2
            + ay_dynamic ** 2
            + az_dynamic ** 2
        )

        # ----------------------------------------------------
        # RPM features
        # ----------------------------------------------------

        rpm_data = rpm_features(rpm)

        # ----------------------------------------------------
        # Basic row
        # ----------------------------------------------------

        row = {

            "file":
                filename,

            "iteration":
                iteration,

            "window":
                window_number,

            "start_time_s":
                (
                    w["timestamp_ms"].iloc[0]
                    - df["timestamp_ms"].iloc[0]
                ) / 1000,

            # ----------------------------------------------
            # Operating condition
            # ----------------------------------------------

            "load_A":
                load_row["load_A"],

            "load_voltage_V":
                load_row["load_voltage_V"],

            "psu_current_A":
                load_row["psu_current_A"],

            "load_power_W":
                load_row["load_power_W"],

            "supply_voltage_V":
                load_row["supply_voltage_V"],

            # ----------------------------------------------
            # AX
            # ----------------------------------------------

            "ax_mean":
                np.mean(ax),

            "ax_std":
                np.std(ax_dynamic),

            "ax_rms":
                rms(ax_dynamic),

            "ax_peak":
                np.max(np.abs(ax_dynamic)),

            "ax_p2p":
                peak_to_peak(ax_dynamic),

            "ax_crest":
                crest_factor(ax_dynamic),

            # ----------------------------------------------
            # AY
            # ----------------------------------------------

            "ay_mean":
                np.mean(ay),

            "ay_std":
                np.std(ay_dynamic),

            "ay_rms":
                rms(ay_dynamic),

            "ay_peak":
                np.max(np.abs(ay_dynamic)),

            "ay_p2p":
                peak_to_peak(ay_dynamic),

            "ay_crest":
                crest_factor(ay_dynamic),

            # ----------------------------------------------
            # AZ
            # ----------------------------------------------

            "az_mean":
                np.mean(az),

            "az_std":
                np.std(az_dynamic),

            "az_rms":
                rms(az_dynamic),

            "az_peak":
                np.max(np.abs(az_dynamic)),

            "az_p2p":
                peak_to_peak(az_dynamic),

            "az_crest":
                crest_factor(az_dynamic),

            # ----------------------------------------------
            # Acceleration magnitude
            # ----------------------------------------------

            "acc_mag_rms":
                rms(magnitude),

            "acc_mag_std":
                np.std(magnitude),

            "acc_mag_peak":
                np.max(np.abs(magnitude)),

            "acc_mag_p2p":
                peak_to_peak(magnitude),

            # ----------------------------------------------
            # ACS712
            # ----------------------------------------------

            "acs_mean":
                np.mean(acs),

            "acs_std":
                np.std(acs),

            "acs_rms":
                rms(acs),

            "acs_min":
                np.min(acs),

            "acs_max":
                np.max(acs),

            "acs_p2p":
                peak_to_peak(acs),

            # ----------------------------------------------
            # RPM
            # ----------------------------------------------

            "rpm_mean":
                rpm_data["rpm_mean"],

            "rpm_median":
                rpm_data["rpm_median"],

            "rpm_std":
                rpm_data["rpm_std"],

            "rpm_min":
                rpm_data["rpm_min"],

            "rpm_max":
                rpm_data["rpm_max"],

            "rpm_p2p":
                rpm_data["rpm_p2p"],

            "rpm_cv_percent":
                rpm_data["rpm_cv_percent"],

            "rpm_valid_fraction":
                rpm_data["rpm_valid_fraction"],

            "rpm_zero_fraction":
                rpm_data["rpm_zero_fraction"],
        }

        # ----------------------------------------------------
        # FFT features
        # ----------------------------------------------------

        (
            dominant_frequency,
            dominant_amplitude,
            spectral_energy,
            spectral_centroid
        ) = spectral_features(
            magnitude,
            FS
        )

        row[
            "dominant_frequency_Hz"
        ] = dominant_frequency

        row[
            "dominant_amplitude"
        ] = dominant_amplitude

        row[
            "spectral_energy"
        ] = spectral_energy

        row[
            "spectral_centroid_Hz"
        ] = spectral_centroid

        results.append(row)

    return results


# ============================================================
# FIND CSV FILES
# ============================================================

csv_files = sorted(
    glob.glob(
        os.path.join(
            RAW_FOLDER,
            "healthy_cc_*A_*.csv"
        )
    )
)

print(
    "\nFound",
    len(csv_files),
    "CSV files."
)

if len(csv_files) == 0:

    raise RuntimeError(
        "No healthy_cc_*A_*.csv files found."
    )


# ============================================================
# PROCESS ALL FILES
# ============================================================

all_results = []

for file_path in csv_files:

    filename = os.path.basename(
        file_path
    )

    # ----------------------------------------------
    # Extract load + iteration
    # ----------------------------------------------

    load_value, iteration = (
        parse_filename(filename)
    )

    # ----------------------------------------------
    # Find matching manual data
    # Match BOTH load and iteration
    # ----------------------------------------------

    matches = load_df[
        np.isclose(
            load_df["load_A"],
            load_value
        )
        &
        (
            load_df["iteration"]
            == iteration
        )
    ]

    if len(matches) != 1:

        raise ValueError(
            f"No unique Excel entry "
            f"for load={load_value} A, iteration{iteration}"
        )

    load_row = matches.iloc[0]

    # ----------------------------------------------
    # Process file
    # ----------------------------------------------

    results = process_file(
        file_path,
        load_row,
        iteration
    )

    all_results.extend(results)


# ============================================================
# CREATE MASTER DATASET
# ============================================================

features_df = pd.DataFrame(
    all_results
)


# ============================================================
# SAVE
# ============================================================

output_file = os.path.join(
    OUTPUT_FOLDER,
    "healthy_features_with_rpm.csv"
)

features_df.to_csv(
    output_file,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n========================================")
print("PROCESSING COMPLETE")
print("========================================")

print(
    "Total CSV files:",
    len(csv_files)
)

print(
    "Total feature windows:",
    len(features_df)
)

print(
    "Output:",
    output_file
)

print("\nColumns:")

for column in features_df.columns:

    print("  ", column)

print("\nFirst rows:")

print(
    features_df.head()
)
