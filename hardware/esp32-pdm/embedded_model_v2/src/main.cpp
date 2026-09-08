#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_NeoPixel.h>

#include "motor_model_v2.h"

constexpr int I2C_SDA_PIN = 8;
constexpr int I2C_SCL_PIN = 9;
constexpr int ACS712_PIN = 4;
constexpr int INDEX_PIN = 6;
constexpr int RGB_LED_PIN = 38;
constexpr int WINDOW_SAMPLES = 200;
constexpr uint32_t SAMPLE_PERIOD_US = 5000;
constexpr uint32_t ENCODER_DEBOUNCE_US = 2000;
constexpr uint32_t MIN_VALID_PERIOD_US = 8000;
constexpr float RPM_HARD_MAX = 5000.0f;
constexpr float RPM_JUMP_LIMIT = 1000.0f;

Adafruit_MPU6050 mpu;
Adafruit_NeoPixel statusLed(1, RGB_LED_PIN, NEO_GRB + NEO_KHZ800);
volatile uint32_t pulsePeriodUs = 0;
volatile uint32_t lastIndexTime = 0;
float axSamples[WINDOW_SAMPLES], aySamples[WINDOW_SAMPLES], azSamples[WINDOW_SAMPLES], rpmSamples[WINDOW_SAMPLES];
int acsSamples[WINDOW_SAMPLES];
int sampleCount = 0;

void setLed(uint8_t r, uint8_t g, uint8_t b) {
  statusLed.setPixelColor(0, statusLed.Color(r, g, b));
  statusLed.show();
}

void setClassLed(int classId) {
  // V2 class order: F1, F2, F3, F4, HEALTHY.
  switch (classId) {
    case 0: setLed(255, 80, 0); break;   // F1 amber
    case 1: setLed(255, 180, 0); break;  // F2 yellow
    case 2: setLed(170, 0, 255); break;  // F3 purple
    case 3: setLed(255, 0, 0); break;    // F4 red
    case 4: setLed(0, 255, 0); break;    // Healthy green
    default: setLed(0, 0, 255); break;   // invalid / collecting blue
  }
}

void IRAM_ATTR indexISR() {
  const uint32_t now = micros();
  if (lastIndexTime == 0) { lastIndexTime = now; return; }
  const uint32_t elapsed = now - lastIndexTime;
  if (elapsed < ENCODER_DEBOUNCE_US) return;
  if (elapsed >= MIN_VALID_PERIOD_US) { pulsePeriodUs = elapsed; lastIndexTime = now; }
}

float currentRpm() {
  uint32_t periodCopy, lastPulseCopy;
  noInterrupts(); periodCopy = pulsePeriodUs; lastPulseCopy = lastIndexTime; interrupts();
  if (lastPulseCopy == 0 || micros() - lastPulseCopy > 2000000) return 0.0f;
  return periodCopy >= MIN_VALID_PERIOD_US ? 60000000.0f / periodCopy : 0.0f;
}

float localRpmMedian(int center) {
  float values[5]; int count = 0;
  const int start = max(0, center - 2), end = min(WINDOW_SAMPLES - 1, center + 2);
  for (int i = start; i <= end; ++i) values[count++] = rpmSamples[i];
  for (int i = 1; i < count; ++i) {
    const float value = values[i]; int j = i - 1;
    while (j >= 0 && values[j] > value) { values[j + 1] = values[j]; --j; }
    values[j + 1] = value;
  }
  return values[count / 2];
}

bool rpmIsValid(int index) {
  const float value = rpmSamples[index];
  if (!isfinite(value) || value <= 0.0f || value > RPM_HARD_MAX) return false;
  if (fabsf(value - localRpmMedian(index)) > RPM_JUMP_LIMIT) return false;
  if (index > 0 && fabsf(value - rpmSamples[index - 1]) > RPM_JUMP_LIMIT) return false;
  if (index + 1 < WINDOW_SAMPLES && fabsf(value - rpmSamples[index + 1]) > RPM_JUMP_LIMIT) return false;
  return true;
}

void sortValues(float values[], int count) {
  for (int i = 1; i < count; ++i) {
    const float value = values[i]; int j = i - 1;
    while (j >= 0 && values[j] > value) { values[j + 1] = values[j]; --j; }
    values[j + 1] = value;
  }
}

void classifyWindow() {
  float axMean = 0, ayMean = 0, azMean = 0, acsMean = 0;
  for (int i = 0; i < WINDOW_SAMPLES; ++i) {
    axMean += axSamples[i]; ayMean += aySamples[i]; azMean += azSamples[i]; acsMean += acsSamples[i];
  }
  axMean /= WINDOW_SAMPLES; ayMean /= WINDOW_SAMPLES; azMean /= WINDOW_SAMPLES; acsMean /= WINDOW_SAMPLES;

  float aySquares = 0, axSquares = 0, axPeak = 0, ayMin = INFINITY, ayMax = -INFINITY, acsSquares = 0;
  for (int i = 0; i < WINDOW_SAMPLES; ++i) {
    const float ay = aySamples[i] - ayMean, ax = axSamples[i] - axMean;
    aySquares += ay * ay; axSquares += ax * ax; acsSquares += float(acsSamples[i]) * acsSamples[i];
    ayMin = min(ayMin, ay); ayMax = max(ayMax, ay); axPeak = max(axPeak, fabsf(ax));
  }
  const float ayRms = sqrtf(aySquares / WINDOW_SAMPLES);
  const float axRms = sqrtf(axSquares / WINDOW_SAMPLES);
  const float axCrest = axRms > 0 ? axPeak / axRms : 0;

  float validRpm[WINDOW_SAMPLES]; int validCount = 0;
  for (int i = 0; i < WINDOW_SAMPLES; ++i) if (rpmIsValid(i)) validRpm[validCount++] = rpmSamples[i];
  if (validCount < WINDOW_SAMPLES / 2) { setLed(0, 0, 255); Serial.println("V2: skipped; insufficient valid RPM"); return; }
  sortValues(validRpm, validCount);
  const float rpmMedian = validCount % 2 ? validRpm[validCount / 2] : (validRpm[validCount / 2 - 1] + validRpm[validCount / 2]) * 0.5f;
  const float features[MOTOR_V2_FEATURE_COUNT] = {
    azMean, validRpm[0], ayRms, ayRms, axCrest, rpmMedian, validRpm[validCount - 1], ayMax - ayMin,
    axRms, axRms, sqrtf(acsSquares / WINDOW_SAMPLES), acsMean
  };
  float confidence = 0;
  const int classId = motorV2Predict(features, &confidence);
  setClassLed(classId);
  Serial.printf("V2 | Prediction: %s | confidence: %.0f%% | RPM %.0f/%.0f/%.0f | ACS mean %.1f\n",
                MOTOR_V2_LABELS[classId], confidence * 100, validRpm[0], rpmMedian,
                validRpm[validCount - 1], acsMean);
}

void setup() {
  Serial.begin(115200); delay(1000);
  statusLed.begin(); statusLed.clear(); statusLed.show(); setLed(0, 0, 255);
  Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN);
  if (!mpu.begin()) { Serial.println("ERROR: MPU6050 not detected"); while (true) delay(1000); }
  mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu.setFilterBandwidth(MPU6050_BAND_94_HZ);
  analogReadResolution(12); analogSetPinAttenuation(ACS712_PIN, ADC_11db);
  pinMode(INDEX_PIN, INPUT_PULLUP); attachInterrupt(digitalPinToInterrupt(INDEX_PIN), indexISR, RISING);
  Serial.println("Embedded Model V2: 25-tree current + vibration + RPM classifier");
}

void loop() {
  static uint32_t lastSampleUs = 0;
  if (micros() - lastSampleUs < SAMPLE_PERIOD_US) return;
  lastSampleUs = micros();
  sensors_event_t accel, gyro, temperature;
  mpu.getEvent(&accel, &gyro, &temperature);
  axSamples[sampleCount] = accel.acceleration.x;
  aySamples[sampleCount] = accel.acceleration.y;
  azSamples[sampleCount] = accel.acceleration.z;
  acsSamples[sampleCount] = analogRead(ACS712_PIN);
  rpmSamples[sampleCount++] = currentRpm();
  if (sampleCount == WINDOW_SAMPLES) { classifyWindow(); sampleCount = 0; }
}
