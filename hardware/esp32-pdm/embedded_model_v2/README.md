# Embedded Model V2

Independent ESP32 deployment project. The original deployment remains in the
parent project. V2 uses a 25-tree compact random forest with vibration, RPM,
and ACS712-current features to reduce F2/F3 confusion.

Build: `pio run -d embedded_model_v2`

Upload: `pio run -d embedded_model_v2 -t upload`

Monitor: `pio device monitor -d embedded_model_v2 --baud 115200`
