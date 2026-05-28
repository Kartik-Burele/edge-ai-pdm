# Dataset Description

The dataset consists of four CSV files, each representing different motor health conditions:

1. **healthy.csv** - Data from healthy motors.
2. **healthy\_zip.csv** - Data from motors with mechanical damage.
3. **faulty.csv** - Data from motors with faults.
4. **faulty\_zip.csv** - Data from motors with both electrical and mechanical damage.
5. **motors.csv** - Merged data from all motors with additional column that contains motor condition.

Detailed analasis is located in `DataAppendix.pdf` file, where we show statistics and distributions of each feature.

### Experiment ID

Each row in the dataset represents an experiment identified by an **Experiment ID**, where each ID corresponds to a 0.8-second signal recording.

## Features

The dataset includes the following key features, extracted from both **current (A) and rotational speed (RPM)** measurements:

### Current (A) Features:

- **CURRENT (A) mean** - The average current over the experiment duration.
- **CURRENT (A) std** - The standard deviation of the current signal.
- **CURRENT (A) max** - The maximum recorded current value.
- **CURRENT (A) rms** - The root mean square (RMS) value of the current.
- **CURRENT (A) peak\_to\_peak** - The difference between the maximum and minimum current values.
- **CURRENT (A) skew** - The skewness of the current distribution.
- **CURRENT (A) kurtosis** - The kurtosis of the current distribution.
- **CURRENT (A) crest\_factor** - The ratio of the maximum current to the RMS value.
- **CURRENT (A) Frequency Center** - The center frequency of the current spectrum.
- **CURRENT (A) Spectrum Area** - The total power in the current spectrum.
- **CURRENT (A) Amp @ 1x RPM** - The amplitude of the current signal at the fundamental rotational frequency.
- **CURRENT (A) Amp @ 2x RPM** - The amplitude of the current signal at the second harmonic of the rotational speed.
- **CURRENT (A) Amp @ 3x RPM** - The amplitude of the current signal at the third harmonic of the rotational speed.

### Rotational Speed (RPM) Features:

- **ROTO (RPM) mean** - The average rotational speed during the experiment.
- **ROTO (RPM) std** - The standard deviation of the rotational speed.
- **ROTO (RPM) max** - The maximum recorded RPM.
- **ROTO (RPM) rms** - The root mean square (RMS) value of the RPM.
- **ROTO (RPM) peak\_to\_peak** - The difference between the maximum and minimum RPM values.
- **ROTO (RPM) skew** - The skewness of the RPM distribution.
- **ROTO (RPM) kurtosis** - The kurtosis of the RPM distribution.
- **ROTO (RPM) crest\_factor** - The ratio of the maximum RPM to the RMS value.
- **ROTO (RPM) Frequency Center** - The center frequency of the RPM spectrum.
- **ROTO (RPM) Spectrum Area** - The total power in the RPM spectrum.
- **ROTO (RPM) Amp @ 1x RPM** - The amplitude of the RPM signal at the fundamental rotational frequency.
- **ROTO (RPM) Amp @ 2x RPM** - The amplitude of the RPM signal at the second harmonic of the rotational speed.
- **ROTO (RPM) Amp @ 3x RPM** - The amplitude of the RPM signal at the third harmonic of the rotational speed.

## Classification of Motor Conditions

The dataset categorizes motors into four different conditions:

1. **Healthy** - No mechanical or electrical damage (stored in `healthy.csv`).
2. **Mechanical Damage** - Indicated by "zip" in the filename (stored in `healthy_zip.csv`).
3. **Electrical Damage** - Motors exhibiting electrical issues (stored in `faulty.csv`).
4. **Both Electrical & Mechanical Damage** - Motors with both types of faults (stored in `faulty_zip.csv`).

In `motors.csv` information about motor's class is in **Class** column, where they are named:
1. **Healthy** - healthy.
2. **Mech_Damage** - mechanical damage.
3. **Elec_Damage** - electrical damage.
4. **Mech_Elec_Damage** - both electrical and mechanical damage.

