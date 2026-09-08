import serial
import csv
import time
from datetime import datetime
 
# ==============================
# USER SETTINGS
# ==============================
 
SERIAL_PORT = "COM12"
BAUD_RATE = 115200
 
# Change this for each experiment
FILE_NAME = "log_file/29_08_26/F4_UV_cc_1A_9V_12V_3.csv"
 
# ==============================
# SERIAL CONNECTION
# ==============================
 
print(f"Opening {SERIAL_PORT}...")
 
ser = serial.Serial(
    SERIAL_PORT,
    BAUD_RATE,
    timeout=1
)
 
time.sleep(2)
 
print("Connected.")
print("Waiting for ESP32 data...")
print("Press Ctrl+C to stop recording.\n")
 
# ==============================
# CSV FILE
# ==============================
 
with open(FILE_NAME, "w", newline="") as csvfile:
 
    writer = csv.writer(csvfile)
 
    # CSV header
    writer.writerow([
        "timestamp_ms",
        "ax",
        "ay",
        "az",
        "acs_adc",
        "rpm"
    ])
 
    sample_count = 0
 
    try:
 
        while True:
 
            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()
 
            if not line:
                continue
 
            # Ignore ESP32 messages
            if not line[0].isdigit():
                continue
 
            values = line.split(",")
 
            # We expect exactly 6 values
            if len(values) != 6:
                continue
 
            try:
                timestamp_ms = int(values[0])
                ax = float(values[1])
                ay = float(values[2])
                az = float(values[3])
                acs_adc = int(values[4])
                rpm = float(values[5])
 
            except ValueError:
                continue
 
            # Write row
            writer.writerow([
                timestamp_ms,
                ax,
                ay,
                az,
                acs_adc,
                rpm
            ])
 
            # Make sure data is written immediately
            csvfile.flush()
 
            sample_count += 1
 
            # Status every 200 samples
            if sample_count % 200 == 0:
 
                print(
                    f"Samples: {sample_count} | "
                    f"Latest: "
                    f"Ax={ax:.3f}, "
                    f"Ay={ay:.3f}, "
                    f"Az={az:.3f}, "
                    f"ADC={acs_adc}, "
                    f"RPM={rpm:.2f}"
                )
 
    except KeyboardInterrupt:
 
        print("\n\nRecording stopped.")
 
    finally:
 
        ser.close()
 
        print(f"Total samples recorded: {sample_count}")
        print(f"File saved as: {FILE_NAME}")
 