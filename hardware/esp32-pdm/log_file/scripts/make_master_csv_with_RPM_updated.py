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

# ---------------- RPM cleaning ----------------
# Keep raw RPM untouched. Invalid samples are converted to NaN
# only in rpm_clean and are flagged by rpm_valid.
RPM_HARD_MIN = 0
RPM_HARD_MAX = 5000          # Change only if your motor can exceed this
RPM_JUMP_LIMIT = 1000       # Maximum reasonable point-to-point jump
RPM_MEDIAN_WINDOW = 5       # Samples (~25 ms at 200 Hz)

# ---------------- Timestamp gap ----------------
# A gap much larger than the normal sample interval is treated
# as a logging discontinuity. Windows crossing a gap are skipped.
TIMESTAMP_GAP_FACTOR = 3.0

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ============================================================
# LOAD MANUAL LOAD DATA
# ============================================================

load_df = pd.read_excel(EXCEL_FILE)

print("\nManual load data:")
print(load_df)

required_load_columns = [
    "iteration",
    "load_A",
    "load_voltage_V",
    "psu_current_A",
    "load_power_W",
    "supply_voltage_V"
]

missing_load_columns = [
    c for c in required_load_columns if c not in load_df.columns
]

if missing_load_columns:
    raise ValueError(
        "Excel is missing columns: "
        + ", ".join(missing_load_columns)
    )


# ============================================================
# FEATURE FUNCTIONS
# ============================================================

def rms(x):
    x = np.asarray(x, dtype=float)
    return np.sqrt(np.mean(x ** 2))


def peak_to_peak(x):
    x = np.asarray(x, dtype=float)
    return np.max(x) - np.min(x)


def crest_factor(x):
    r = rms(x)

    if r == 0:
        return 0

    return np.max(np.abs(x)) / r


def spectral_features(x, fs):
    n = len(x)

    x = x - np.mean(x)

    window = np.hanning(n)
    x_windowed = x * window

    spectrum = np.fft.rfft(x_windowed)
    magnitude = np.abs(spectrum)

    frequencies = np.fft.rfftfreq(n, d=1 / fs)

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
# RPM CLEANING
# ============================================================

def clean_rpm(rpm):
    """
    Keep the original RPM in rpm_raw.

    rpm_clean:
        Valid RPM values only. Suspected encoder glitches
        become NaN.

    rpm_valid:
        1 = accepted sample
        0 = rejected sample

    Detection:
        1. non-positive values
        2. impossible absolute RPM
        3. isolated/sudden jumps relative to a short
           rolling median
        4. large point-to-point jumps
    """

    raw = np.asarray(rpm, dtype=float)

    clean = raw.copy()

    valid = np.isfinite(raw)

    # --------------------------------------------------------
    # Absolute physical limits
    # --------------------------------------------------------

    valid &= raw > RPM_HARD_MIN
    valid &= raw <= RPM_HARD_MAX

    # --------------------------------------------------------
    # Short rolling median
    # This follows real speed changes but suppresses isolated
    # encoder glitches.
    # --------------------------------------------------------

    series = pd.Series(raw)

    rolling_median = (
        series
        .rolling(
            window=RPM_MEDIAN_WINDOW,
            center=True,
            min_periods=1
        )
        .median()
        .to_numpy()
    )

    # Only reject large deviations where the local median
    # itself is meaningful.
    median_valid = np.isfinite(rolling_median)

    deviation = np.abs(raw - rolling_median)

    valid &= (
        (~median_valid)
        | (deviation <= RPM_JUMP_LIMIT)
    )

    # --------------------------------------------------------
    # Point-to-point jump check
    # --------------------------------------------------------

    if len(raw) > 1:
        jump = np.abs(np.diff(raw))

        jump_invalid = np.zeros(len(raw), dtype=bool)

        jump_invalid[1:] |= (
            jump > RPM_JUMP_LIMIT
        )

        jump_invalid[:-1] |= (
            jump > RPM_JUMP_LIMIT
        )

        valid &= ~jump_invalid

    clean[~valid] = np.nan

    return clean, valid.astype(int)


def rpm_features(rpm_clean):
    """
    Calculate RPM features using only accepted samples.
    """

    rpm = np.asarray(rpm_clean, dtype=float)

    valid_rpm = rpm[np.isfinite(rpm)]

    total_samples = len(rpm)
    valid_samples = len(valid_rpm)

    if valid_samples == 0:
        return {
            "rpm_mean": np.nan,
            "rpm_median": np.nan,
            "rpm_std": np.nan,
            "rpm_min": np.nan,
            "rpm_max": np.nan,
            "rpm_p2p": np.nan,
            "rpm_cv_percent": np.nan,
            "rpm_valid_fraction": 0,
            "rpm_invalid_fraction": 1,
            "rpm_slope_rpm_per_s": np.nan,
        }

    rpm_mean = np.mean(valid_rpm)
    rpm_std = np.std(valid_rpm)

    rpm_cv = (
        rpm_std / rpm_mean * 100
        if rpm_mean > 0 else np.nan
    )

    # Linear slope over the window, useful for load
    # transients / speed recovery.
    valid_indices = np.where(np.isfinite(rpm))[0]

    if len(valid_indices) >= 2:
        t = valid_indices / FS
        slope = np.polyfit(t, rpm[valid_indices], 1)[0]
    else:
        slope = np.nan

    return {
        "rpm_mean": rpm_mean,
        "rpm_median": np.median(valid_rpm),
        "rpm_std": rpm_std,
        "rpm_min": np.min(valid_rpm),
        "rpm_max": np.max(valid_rpm),
        "rpm_p2p": np.max(valid_rpm) - np.min(valid_rpm),
        "rpm_cv_percent": rpm_cv,
        "rpm_valid_fraction": valid_samples / total_samples,
        "rpm_invalid_fraction": 1 - (valid_samples / total_samples),
        "rpm_slope_rpm_per_s": slope,
    }


# ============================================================
# FILENAME PARSING
# ============================================================

def parse_healthy_filename(filename):
    """
    Expected:
        healthy_cc_01A_1.csv
        healthy_cc_10A_3.csv
        healthy_cc_20A_2.csv
    """

    pattern = r"healthy_cc_(\d+)A_(\d+)\.csv"
    match = re.match(pattern, filename, re.IGNORECASE)

    if not match:
        raise ValueError(
            f"Unexpected healthy filename format: {filename}"
        )

    load_number = int(match.group(1))
    iteration = int(match.group(2))

    return load_number / 10.0, iteration


def parse_fault_filename(filename):
    """
    Expected examples:
        F1_repeat_cc_0.4_0.8A_1.csv
        F2_stepup_cc_0.3_1A_2.csv
        F3_spike_cc_0.2_1A_3.csv
        F4_UV_cc_1A_9V_12V_1.csv

    Fault load values are descriptive only. The operating
    condition in the CSV is retained from the logger data.
    """

    pattern = r"(F[1-4])_(.+)_(\d+)\.csv"
    match = re.match(pattern, filename, re.IGNORECASE)

    if not match:
        raise ValueError(
            f"Unexpected fault filename format: {filename}"
        )

    fault_id = match.group(1).upper()
    description = match.group(2)
    iteration = int(match.group(3))

    return fault_id, description, iteration


# ============================================================
# LOAD CONDITION MATCHING
# ============================================================

def find_healthy_load_row(load_value, iteration):
    """
    Healthy Excel contains repeated measurements for each load,
    so match BOTH load_A and iteration.
    """

    matches = load_df[
        np.isclose(
            load_df["load_A"].astype(float),
            load_value
        )
        &
        (
            load_df["iteration"].astype(int)
            == int(iteration)
        )
    ]

    if len(matches) != 1:
        raise ValueError(
            f"No unique Excel entry for "
            f"load={load_value} A, iteration={iteration}. "
            f"Found {len(matches)} rows."
        )

    return matches.iloc[0]


# ============================================================
# TIMESTAMP SEGMENTS
# ============================================================

def find_continuous_segments(timestamps):
    """
    Returns continuous row ranges.

    A new segment starts after a timestamp gap greater than
    TIMESTAMP_GAP_FACTOR * median sample interval.
    """

    timestamps = np.asarray(timestamps, dtype=float)

    if len(timestamps) < 2:
        return [(0, len(timestamps))], 0, np.nan

    dt = np.diff(timestamps)

    positive_dt = dt[dt > 0]

    if len(positive_dt) == 0:
        return [(0, len(timestamps))], 0, np.nan

    median_dt = np.median(positive_dt)

    gap_threshold = (
        TIMESTAMP_GAP_FACTOR
        * median_dt
    )

    gap_indices = np.where(
        dt > gap_threshold
    )[0]

    segments = []

    start = 0

    for gap_index in gap_indices:
        end = gap_index + 1

        if end - start >= WINDOW_SAMPLES:
            segments.append((start, end))

        start = end

    if len(timestamps) - start >= WINDOW_SAMPLES:
        segments.append(
            (start, len(timestamps))
        )

    estimated_fs = 1000.0 / median_dt

    return segments, len(gap_indices), estimated_fs


# ============================================================
# PROCESS ONE CSV
# ============================================================

def process_file(
    file_path,
    load_row,
    iteration,
    dataset_type,
    fault_id="HEALTHY",
    fault_description=""
):

    filename = os.path.basename(file_path)

    print("\nProcessing:", filename)

    df = pd.read_csv(file_path)

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

    timestamps = df["timestamp_ms"].to_numpy()

    segments, gap_count, estimated_fs = (
        find_continuous_segments(timestamps)
    )

    duration = (
        timestamps[-1]
        - timestamps[0]
    ) / 1000.0

    print(
        f"Samples = {len(df)}, "
        f"Duration = {duration:.3f}s, "
        f"Estimated Fs = {estimated_fs:.2f} Hz, "
        f"Timestamp gaps = {gap_count}"
    )

    if gap_count > 0:
        print(
            "WARNING: timestamp discontinuity detected. "
            "Windows crossing the gap will be skipped."
        )

    # --------------------------------------------------------
    # Clean RPM once for the entire file
    # --------------------------------------------------------

    rpm_raw_all = df["rpm"].to_numpy(dtype=float)

    rpm_clean_all, rpm_valid_all = clean_rpm(
        rpm_raw_all
    )

    invalid_fraction = (
        1 - np.mean(rpm_valid_all)
    )

    print(
        f"RPM invalid fraction = "
        f"{invalid_fraction:.2%}"
    )

    results = []

    # --------------------------------------------------------
    # Process only continuous segments
    # --------------------------------------------------------

    window_global_number = 0

    for segment_id, (segment_start, segment_end) in enumerate(
        segments
    ):

        segment_length = (
            segment_end - segment_start
        )

        number_of_windows = (
            segment_length // WINDOW_SAMPLES
        )

        for local_window_number in range(
            number_of_windows
        ):

            start = (
                segment_start
                + local_window_number
                * WINDOW_SAMPLES
            )

            end = (
                start
                + WINDOW_SAMPLES
            )

            w = df.iloc[start:end].copy()

            ax = w["ax"].to_numpy()
            ay = w["ay"].to_numpy()
            az = w["az"].to_numpy()
            acs = w["acs_adc"].to_numpy()

            rpm_raw = rpm_raw_all[start:end]
            rpm_clean = rpm_clean_all[start:end]
            rpm_valid = rpm_valid_all[start:end]

            # ------------------------------------------------
            # Acceleration dynamic component
            # ------------------------------------------------

            ax_dynamic = ax - np.mean(ax)
            ay_dynamic = ay - np.mean(ay)
            az_dynamic = az - np.mean(az)

            magnitude = np.sqrt(
                ax_dynamic ** 2
                + ay_dynamic ** 2
                + az_dynamic ** 2
            )

            # ------------------------------------------------
            # RPM features
            # ------------------------------------------------

            rpm_data = rpm_features(
                rpm_clean
            )

            # ------------------------------------------------
            # Basic row
            # ------------------------------------------------

            row = {

                "dataset_type":
                    dataset_type,

                "fault_id":
                    fault_id,

                "fault_description":
                    fault_description,

                "file":
                    filename,

                "iteration":
                    iteration,

                "segment":
                    segment_id,

                "window":
                    window_global_number,

                "start_time_s":
                    (
                        w["timestamp_ms"].iloc[0]
                        - df["timestamp_ms"].iloc[0]
                    ) / 1000,

                # ------------------------------------------
                # Operating condition
                # ------------------------------------------

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

                # ------------------------------------------
                # AX
                # ------------------------------------------

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

                # ------------------------------------------
                # AY
                # ------------------------------------------

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

                # ------------------------------------------
                # AZ
                # ------------------------------------------

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

                # ------------------------------------------
                # Acceleration magnitude
                # ------------------------------------------

                "acc_mag_rms":
                    rms(magnitude),

                "acc_mag_std":
                    np.std(magnitude),

                "acc_mag_peak":
                    np.max(np.abs(magnitude)),

                "acc_mag_p2p":
                    peak_to_peak(magnitude),

                # ------------------------------------------
                # ACS712
                # ------------------------------------------

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

                # ------------------------------------------
                # RPM raw quality information
                # ------------------------------------------

                "rpm_raw_mean":
                    np.mean(rpm_raw),

                "rpm_raw_median":
                    np.median(rpm_raw),

                "rpm_invalid_samples":
                    int(np.sum(rpm_valid == 0)),

                # ------------------------------------------
                # RPM cleaned features
                # ------------------------------------------

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

                "rpm_invalid_fraction":
                    rpm_data["rpm_invalid_fraction"],

                "rpm_slope_rpm_per_s":
                    rpm_data["rpm_slope_rpm_per_s"],
            }

            # ------------------------------------------------
            # FFT features
            # ------------------------------------------------

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

            window_global_number += 1

    return results


# ============================================================
# FIND HEALTHY FILES
# ============================================================

healthy_files = sorted(
    glob.glob(
        os.path.join(
            RAW_FOLDER,
            "healthy_cc_*A_*.csv"
        )
    )
)


# ============================================================
# FIND FAULT FILES
# ============================================================

fault_files = sorted(
    glob.glob(
        os.path.join(
            RAW_FOLDER,
            "F[1-4]_*.csv"
        )
    )
)


print(
    "\nFound",
    len(healthy_files),
    "healthy CSV files."
)

print(
    "Found",
    len(fault_files),
    "fault CSV files."
)

if (
    len(healthy_files) == 0
    and len(fault_files) == 0
):
    raise RuntimeError(
        "No healthy or fault CSV files found."
    )


# ============================================================
# PROCESS HEALTHY DATA
# ============================================================

all_results = []

for file_path in healthy_files:

    filename = os.path.basename(file_path)

    load_value, iteration = (
        parse_healthy_filename(filename)
    )

    load_row = find_healthy_load_row(
        load_value,
        iteration
    )

    results = process_file(
        file_path=file_path,
        load_row=load_row,
        iteration=iteration,
        dataset_type="healthy",
        fault_id="HEALTHY",
        fault_description=""
    )

    all_results.extend(results)


# ============================================================
# PROCESS FAULT DATA
# ============================================================

# Fault CSVs do not necessarily have a corresponding row in
# the healthy Excel table. Therefore, the operating condition
# is inferred from the measured logger data where possible.
#
# For now, fault load/voltage/power/PSU-current are left NaN.
# This prevents us from accidentally assigning a healthy
# operating point to a transient fault experiment.
#
# We will add measured fault-condition metadata separately
# once you provide the transient load table.

fault_default_row = {
    "load_A": np.nan,
    "load_voltage_V": np.nan,
    "psu_current_A": np.nan,
    "load_power_W": np.nan,
    "supply_voltage_V": np.nan
}

for file_path in fault_files:

    filename = os.path.basename(file_path)

    fault_id, fault_description, iteration = (
        parse_fault_filename(filename)
    )

    results = process_file(
        file_path=file_path,
        load_row=fault_default_row,
        iteration=iteration,
        dataset_type="fault",
        fault_id=fault_id,
        fault_description=fault_description
    )

    all_results.extend(results)


# ============================================================
# CREATE MASTER DATASET
# ============================================================

features_df = pd.DataFrame(
    all_results
)


# ============================================================
# SAVE MASTER DATASET
# ============================================================

output_file = os.path.join(
    OUTPUT_FOLDER,
    "master_features_with_rpm.csv"
)

features_df.to_csv(
    output_file,
    index=False
)


# ============================================================
# SAVE RPM QUALITY REPORT
# ============================================================

rpm_quality = (
    features_df[
        [
            "dataset_type",
            "fault_id",
            "file",
            "iteration",
            "segment",
            "window",
            "rpm_raw_mean",
            "rpm_raw_median",
            "rpm_mean",
            "rpm_median",
            "rpm_invalid_samples",
            "rpm_valid_fraction"
        ]
    ]
    .copy()
)

quality_file = os.path.join(
    OUTPUT_FOLDER,
    "rpm_quality_report.csv"
)

rpm_quality.to_csv(
    quality_file,
    index=False
)


# ============================================================
# SUMMARY
# ============================================================

print("\n========================================")
print("PROCESSING COMPLETE")
print("========================================")

print(
    "Healthy CSV files:",
    len(healthy_files)
)

print(
    "Fault CSV files:",
    len(fault_files)
)

print(
    "Total feature windows:",
    len(features_df)
)

print(
    "Master output:",
    output_file
)

print(
    "RPM quality report:",
    quality_file
)

print("\nDataset counts:")

print(
    features_df["dataset_type"]
    .value_counts()
)

print("\nFault counts:")

print(
    features_df["fault_id"]
    .value_counts()
)

print("\nRPM quality summary:")

print(
    features_df[
        [
            "rpm_valid_fraction",
            "rpm_invalid_fraction"
        ]
    ].describe()
)

print("\nFirst rows:")

print(
    features_df.head()
)
