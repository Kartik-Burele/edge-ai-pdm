/**
 * Enhanced Predictive Maintenance: Real-Time Edge Classifier
 * Board: ESP32-S3 DevKitC-1
 * 
 * Features:
 * - 200 Hz sensor acquisition (MPU6050 Accelerometer, ACS712 ADC, Optical Encoder)
 * - 200-sample circular ring buffer
 * - 250 ms sub-second rolling window inference (4 predictions / sec)
 * - Automatic startup zero-current baseline calibration
 * - NeoPixel RGB status LED signaling
 * - High-speed JSON telemetry stream over UART (115200 baud)
 */

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_NeoPixel.h>

#include "pdm_model.h"

// Hardware Pin Definitions
#define I2C_SDA_PIN 8
#define I2C_SCL_PIN 9
#define ACS712_ADC_PIN 4
#define ENCODER_INDEX_PIN 6
#define RGB_STATUS_LED_PIN 38

// Sampling & Buffer Configuration
constexpr uint32_t SAMPLE_PERIOD_US = 5000;    // 200 Hz (5000 us)
constexpr int BUFFER_SIZE = 200;                // 1.0 second history
constexpr int INFERENCE_STRIDE = 50;            // Run inference every 50 samples (250 ms)
constexpr uint32_t ENCODER_DEBOUNCE_US = 2000;
constexpr uint32_t MIN_VALID_PERIOD_US = 8000;
constexpr float RPM_HARD_MAX = 5000.0f;
constexpr float RPM_JUMP_LIMIT = 1000.0f;

// Global Objects & State
Adafruit_MPU6050 mpu;
Adafruit_NeoPixel statusLed(1, RGB_STATUS_LED_PIN, NEO_GRB + NEO_KHZ800);

volatile uint32_t g_last_pulse_us = 0;
volatile uint32_t g_pulse_period_us = 0;

float ax_ring[BUFFER_SIZE];
float ay_ring[BUFFER_SIZE];
float az_ring[BUFFER_SIZE];
float acs_ring[BUFFER_SIZE];
float rpm_ring[BUFFER_SIZE];

int write_index = 0;
int samples_accumulated = 0;
int stride_counter = 0;
float acs_zero_offset = 0.0f;

// ----------------------------------------------------------------------------
// LED Status Indicator & Temporal Smoothing
// ----------------------------------------------------------------------------
constexpr int DEBOUNCE_HISTORY_LEN = 3;
int pred_history[DEBOUNCE_HISTORY_LEN] = {4, 4, 4}; // Default to HEALTHY (index 4)
int history_idx = 0;

void setStatusColor(uint8_t r, uint8_t g, uint8_t b) {
  statusLed.setPixelColor(0, statusLed.Color(r, g, b));
  statusLed.show();
}

int getSmoothedClass(int current_pred) {
  pred_history[history_idx] = current_pred;
  history_idx = (history_idx + 1) % DEBOUNCE_HISTORY_LEN;

  // Check for majority vote in history
  int votes[PDM_CLASS_COUNT] = {0};
  for (int i = 0; i < DEBOUNCE_HISTORY_LEN; ++i) {
    votes[pred_history[i]]++;
  }

  int best_c = current_pred;
  int max_v = 0;
  for (int c = 0; c < PDM_CLASS_COUNT; ++c) {
    if (votes[c] > max_v) {
      max_v = votes[c];
      best_c = c;
    }
  }
  return best_c;
}

void updateClassLed(int raw_class_id, float health_index) {
  const int class_id = getSmoothedClass(raw_class_id);

  // Exact mapping matching PDM_LABELS in pdm_model.h:
  // 0: "F1"      -> Amber  (255, 120, 0)
  // 1: "F2"      -> Yellow (255, 220, 0)
  // 2: "F3"      -> Purple (180, 0, 255)
  // 3: "F4"      -> Red    (255, 0, 0)
  // 4: "HEALTHY" -> Green  (0, 255, 0)
  switch (class_id) {
    case 0: // F1: Repeat Load Step
      setStatusColor(255, 120, 0); // Amber
      break;
    case 1: // F2: Step Load Increase
      setStatusColor(255, 220, 0); // Yellow
      break;
    case 2: // F3: Current Spike
      setStatusColor(180, 0, 255); // Purple
      break;
    case 3: // F4: Undervoltage
      setStatusColor(255, 0, 0);   // Red
      break;
    case 4: // HEALTHY
      setStatusColor(0, 255, 0);   // Bright Green
      break;
    default:
      setStatusColor(0, 0, 255);   // Blue: Unknown / Uncalibrated
      break;
  }
}

// ----------------------------------------------------------------------------
// Optical Encoder ISR & RPM Tracking
// ----------------------------------------------------------------------------
void IRAM_ATTR encoderISR() {
  const uint32_t now = micros();
  if (g_last_pulse_us == 0) {
    g_last_pulse_us = now;
    return;
  }
  const uint32_t dt = now - g_last_pulse_us;
  if (dt < ENCODER_DEBOUNCE_US) return;
  if (dt >= MIN_VALID_PERIOD_US) {
    g_pulse_period_us = dt;
    g_last_pulse_us = now;
  }
}

float readInstantaneousRpm() {
  uint32_t period_us;
  uint32_t last_time;
  noInterrupts();
  period_us = g_pulse_period_us;
  last_time = g_last_pulse_us;
  interrupts();

  if (last_time == 0 || (micros() - last_time > 2000000)) {
    return 0.0f; // Motor stopped
  }
  return period_us >= MIN_VALID_PERIOD_US ? (60000000.0f / (float)period_us) : 0.0f;
}

// ----------------------------------------------------------------------------
// Static Working Buffers (Stored in DRAM, 0 bytes on stack)
// ----------------------------------------------------------------------------
static float s_ax[BUFFER_SIZE];
static float s_ay[BUFFER_SIZE];
static float s_az[BUFFER_SIZE];
static float s_acs[BUFFER_SIZE];
static float s_rpm[BUFFER_SIZE];
static float s_valid_rpm[BUFFER_SIZE];
static float s_valid_t[BUFFER_SIZE];
static float s_valid_rpm_sorted[BUFFER_SIZE];

// Iterative in-place insertion sort (Zero stack usage, no recursion)
void insertionSort(float arr[], int n) {
  for (int i = 1; i < n; ++i) {
    const float key = arr[i];
    int j = i - 1;
    while (j >= 0 && arr[j] > key) {
      arr[j + 1] = arr[j];
      --j;
    }
    arr[j + 1] = key;
  }
}

// ----------------------------------------------------------------------------
// Feature Extraction & Inference
// ----------------------------------------------------------------------------
void processRollingWindow() {
  float az_sum = 0.0f, ay_sum = 0.0f, ax_sum = 0.0f, acs_sum = 0.0f;
  float acs_min = 1e6f, acs_max = -1e6f;

  for (int i = 0; i < BUFFER_SIZE; ++i) {
    const int idx = (write_index + i) % BUFFER_SIZE;
    s_ax[i] = ax_ring[idx];
    s_ay[i] = ay_ring[idx];
    s_az[i] = az_ring[idx];
    s_acs[i] = acs_ring[idx];
    s_rpm[i] = rpm_ring[idx];

    ax_sum += s_ax[i];
    ay_sum += s_ay[i];
    az_sum += s_az[i];
    acs_sum += s_acs[i];
    acs_min = min(acs_min, s_acs[i]);
    acs_max = max(acs_max, s_acs[i]);
  }

  const float ax_mean = ax_sum / (float)BUFFER_SIZE;
  const float ay_mean = ay_sum / (float)BUFFER_SIZE;
  const float az_mean = az_sum / (float)BUFFER_SIZE;
  const float acs_mean = acs_sum / (float)BUFFER_SIZE;
  const float acs_p2p = acs_max - acs_min;

  // ACS712 Current rate of change slope (dI/dt)
  float num_acs = 0.0f;
  for (int i = 0; i < BUFFER_SIZE; ++i) {
    const float dt = ((float)i / 200.0f) - 0.4975f;
    num_acs += dt * (s_acs[i] - acs_mean);
  }
  const float acs_dI_dt_slope = num_acs / 16.66625f;

  // Dynamic signals, RMS, Peak, P2P, Crest
  float ay_sq_sum = 0.0f, az_sq_sum = 0.0f, ax_sq_sum = 0.0f;
  float ay_min = 1e6f, ay_max = -1e6f;
  float az_min = 1e6f, az_max = -1e6f;
  float ax_peak = 0.0f;

  for (int i = 0; i < BUFFER_SIZE; ++i) {
    const float ax_d = s_ax[i] - ax_mean;
    const float ay_d = s_ay[i] - ay_mean;
    const float az_d = s_az[i] - az_mean;

    ax_sq_sum += ax_d * ax_d;
    ax_peak = max(ax_peak, fabsf(ax_d));

    ay_sq_sum += ay_d * ay_d;
    ay_min = min(ay_min, ay_d);
    ay_max = max(ay_max, ay_d);

    az_sq_sum += az_d * az_d;
    az_min = min(az_min, az_d);
    az_max = max(az_max, az_d);
  }

  const float ax_rms = sqrtf(ax_sq_sum / (float)BUFFER_SIZE);
  const float ax_crest = ax_rms > 1e-6f ? ax_peak / ax_rms : 0.0f;

  const float ay_rms = sqrtf(ay_sq_sum / (float)BUFFER_SIZE);
  const float ay_p2p = ay_max - ay_min;

  const float az_std = sqrtf(az_sq_sum / (float)BUFFER_SIZE);

  // RPM validation, statistics, and linear slope
  int valid_count = 0;
  float rpm_sum = 0.0f, t_sum = 0.0f;

  for (int i = 0; i < BUFFER_SIZE; ++i) {
    if (s_rpm[i] > 0.0f && s_rpm[i] <= RPM_HARD_MAX) {
      const float t_sec = (float)i / 200.0f;
      s_valid_rpm[valid_count] = s_rpm[i];
      s_valid_t[valid_count] = t_sec;
      s_valid_rpm_sorted[valid_count] = s_rpm[i];
      rpm_sum += s_rpm[i];
      t_sum += t_sec;
      valid_count++;
    }
  }

  if (valid_count < BUFFER_SIZE / 3) {
    setStatusColor(0, 0, 255); // Blue: Insufficient valid RPM samples
    return;
  }

  // Calculate RPM slope (acceleration/deceleration)
  const float t_mean_rpm = t_sum / (float)valid_count;
  const float rpm_mean_val = rpm_sum / (float)valid_count;
  float num_rpm = 0.0f, den_rpm = 0.0f;
  for (int i = 0; i < valid_count; ++i) {
    const float dt = s_valid_t[i] - t_mean_rpm;
    num_rpm += dt * (s_valid_rpm[i] - rpm_mean_val);
    den_rpm += dt * dt;
  }
  const float rpm_slope_rpm_per_s = den_rpm > 1e-6f ? (num_rpm / den_rpm) : 0.0f;

  insertionSort(s_valid_rpm_sorted, valid_count);
  const float rpm_min = s_valid_rpm_sorted[0];
  const float rpm_max = s_valid_rpm_sorted[valid_count - 1];
  const float rpm_p2p = rpm_max - rpm_min;
  const float rpm_median = valid_count % 2 ? s_valid_rpm_sorted[valid_count / 2] : (s_valid_rpm_sorted[valid_count / 2 - 1] + s_valid_rpm_sorted[valid_count / 2]) * 0.5f;

  // Order 2X Energy on acceleration magnitude
  const float f_2x = (rpm_median / 60.0f) * 2.0f;
  float order_2x_energy = 0.0f;
  if (f_2x > 0.0f && f_2x < 100.0f) {
    float real_sum = 0.0f, imag_sum = 0.0f;
    const float omega = 2.0f * (float)M_PI * f_2x / 200.0f;
    for (int i = 0; i < BUFFER_SIZE; ++i) {
      const float ax_d = s_ax[i] - ax_mean;
      const float ay_d = s_ay[i] - ay_mean;
      const float az_d = s_az[i] - az_mean;
      const float mag_d = sqrtf(ax_d * ax_d + ay_d * ay_d + az_d * az_d);
      const float hanning = 0.5f * (1.0f - cosf(2.0f * (float)M_PI * i / (BUFFER_SIZE - 1)));
      real_sum += (mag_d * hanning) * cosf(omega * i);
      imag_sum -= (mag_d * hanning) * sinf(omega * i);
    }
    order_2x_energy = (real_sum * real_sum + imag_sum * imag_sum);
  }

  // Populate 12-feature vector in exact header order matching pdm_model.h:
  // 0: rpm_min, 1: rpm_median, 2: rpm_slope_rpm_per_s, 3: rpm_p2p,
  // 4: acs_dI_dt_slope, 5: acs_p2p, 6: az_mean, 7: ay_rms,
  // 8: ay_p2p, 9: ax_crest, 10: order_2x_energy, 11: az_std
  const float features[PDM_FEATURE_COUNT] = {
      rpm_min,
      rpm_median,
      rpm_slope_rpm_per_s,
      rpm_p2p,
      acs_dI_dt_slope,
      acs_p2p,
      az_mean,
      ay_rms,
      ay_p2p,
      ax_crest,
      order_2x_energy,
      az_std,
  };

  float confidence = 0.0f;
  float health_index = 100.0f;
  const int pred_class = pdmPredict(features, &confidence, &health_index);

  updateClassLed(pred_class, health_index);

  // High-Speed JSON Telemetry Stream
  Serial.printf(
      "{\"ts\":%lu,\"pred\":\"%s\",\"health\":%.1f,\"conf\":%.1f,\"rpm\":%.1f,\"slope\":%.1f,\"dI_dt\":%.1f}\n",
      millis(),
      PDM_LABELS[pred_class],
      health_index,
      confidence * 100.0f,
      rpm_median,
      rpm_slope_rpm_per_s,
      acs_dI_dt_slope
  );
}

// ----------------------------------------------------------------------------
// Startup Initialization
// ----------------------------------------------------------------------------
void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n--- DC Motor Enhanced Predictive Maintenance Node ---");

  statusLed.begin();
  statusLed.clear();
  setStatusColor(0, 0, 255); // Blue during calibration

  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  if (!mpu.begin()) {
    Serial.println("ERROR: MPU6050 accelerometer not detected over I2C!");
    while (true) {
      setStatusColor(255, 0, 0); delay(200);
      setStatusColor(0, 0, 0); delay(200);
    }
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu.setFilterBandwidth(MPU6050_BAND_94_HZ);

  analogReadResolution(12);
  analogSetPinAttenuation(ACS712_ADC_PIN, ADC_11db);

  pinMode(ENCODER_INDEX_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(ENCODER_INDEX_PIN), encoderISR, RISING);

  // Automatic Zero-Current Calibration
  uint32_t adc_sum = 0;
  for (int i = 0; i < 200; ++i) {
    adc_sum += analogRead(ACS712_ADC_PIN);
    delayMicroseconds(1000);
  }
  acs_zero_offset = (float)adc_sum / 200.0f;
  Serial.printf("ACS712 Zero Calibration Offset: %.1f ADC counts\n", acs_zero_offset);

  setStatusColor(0, 255, 0); // Green when ready
  Serial.println("Sampling started @ 200 Hz with 250 ms rolling inference.");
}

// ----------------------------------------------------------------------------
// Main Loop
// ----------------------------------------------------------------------------
void loop() {
  static uint32_t last_sample_us = 0;
  const uint32_t now = micros();
  if (now - last_sample_us < SAMPLE_PERIOD_US) return;
  last_sample_us = now;

  sensors_event_t accel, gyro, temp;
  mpu.getEvent(&accel, &gyro, &temp);

  ax_ring[write_index] = accel.acceleration.x;
  ay_ring[write_index] = accel.acceleration.y;
  az_ring[write_index] = accel.acceleration.z;
  acs_ring[write_index] = (float)analogRead(ACS712_ADC_PIN) - acs_zero_offset;
  rpm_ring[write_index] = readInstantaneousRpm();

  write_index = (write_index + 1) % BUFFER_SIZE;
  if (samples_accumulated < BUFFER_SIZE) {
    samples_accumulated++;
  } else {
    stride_counter++;
    if (stride_counter >= INFERENCE_STRIDE) {
      processRollingWindow();
      stride_counter = 0;
    }
  }
}
