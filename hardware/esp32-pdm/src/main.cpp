/**
 * Enhanced Predictive Maintenance + Wi-Fi Dashboard
 * Board: ESP32-S3 DevKitC-1
 *
 * Features:
 * - 200 Hz sensor acquisition
 * - MPU6050 accelerometer
 * - ACS712 current sensing
 * - Optical encoder RPM
 * - 200-sample circular buffer
 * - 250 ms rolling-window ML inference
 * - Temporal prediction smoothing
 * - NeoPixel status LED
 * - Serial JSON telemetry
 * - Wi-Fi connection to existing router
 * - Built-in HTTP dashboard
 * - JSON API at /api/data
 *
 * Architecture:
 *
 * Sensors
 *    ↓
 * Feature Extraction
 *    ↓
 * pdmPredict()        <-- AI inference remains on ESP32
 *    ↓
 * Prediction / Health / Confidence
 *    ↓
 * Wi-Fi HTTP Server
 *    ↓
 * Laptop Browser Dashboard
 */

#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_NeoPixel.h>

#include "pdm_model.h"

// ============================================================================
// Wi-Fi Configuration
// ============================================================================

const char* WIFI_SSID = "JetsonHotspot";
const char* WIFI_PASSWORD = "12345678";

WebServer server(80);

// ============================================================================
// Hardware Pin Definitions
// ============================================================================

#define I2C_SDA_PIN       8
#define I2C_SCL_PIN       9
#define ACS712_ADC_PIN    4
#define ENCODER_INDEX_PIN 6
#define RGB_STATUS_LED_PIN 38

// ============================================================================
// Sampling & Buffer Configuration
// ============================================================================

constexpr uint32_t SAMPLE_PERIOD_US = 5000;   // 200 Hz
constexpr int BUFFER_SIZE = 200;              // 1 second
constexpr int INFERENCE_STRIDE = 50;          // 250 ms

constexpr uint32_t ENCODER_DEBOUNCE_US = 2000;
constexpr uint32_t MIN_VALID_PERIOD_US = 8000;

constexpr float RPM_HARD_MAX = 5000.0f;
constexpr float RPM_JUMP_LIMIT = 1000.0f;

// ============================================================================
// Global Hardware Objects
// ============================================================================

Adafruit_MPU6050 mpu;

Adafruit_NeoPixel statusLed(
    1,
    RGB_STATUS_LED_PIN,
    NEO_GRB + NEO_KHZ800
);

// ============================================================================
// Encoder State
// ============================================================================

volatile uint32_t g_last_pulse_us = 0;
volatile uint32_t g_pulse_period_us = 0;

// ============================================================================
// Sensor Ring Buffers
// ============================================================================

float ax_ring[BUFFER_SIZE];
float ay_ring[BUFFER_SIZE];
float az_ring[BUFFER_SIZE];
float acs_ring[BUFFER_SIZE];
float rpm_ring[BUFFER_SIZE];

int write_index = 0;
int samples_accumulated = 0;
int stride_counter = 0;

float acs_zero_offset = 0.0f;

// ============================================================================
// Prediction State
// These variables are sent to the laptop dashboard.
// ============================================================================

volatile int g_prediction_class = 4;

float g_health_index = 100.0f;
float g_confidence = 0.0f;

float g_rpm = 0.0f;
float g_rpm_slope = 0.0f;
float g_current_slope = 0.0f;

float g_temperature = 0.0f;

uint32_t g_prediction_timestamp = 0;

bool g_prediction_available = false;

// ============================================================================
// Prediction History / Smoothing
// ============================================================================

constexpr int DEBOUNCE_HISTORY_LEN = 3;

int pred_history[DEBOUNCE_HISTORY_LEN] = {4, 4, 4};
int history_idx = 0;

// ============================================================================
// LED
// ============================================================================

void setStatusColor(uint8_t r, uint8_t g, uint8_t b)
{
    statusLed.setPixelColor(
        0,
        statusLed.Color(r, g, b)
    );

    statusLed.show();
}

// ============================================================================
// Prediction Smoothing
// ============================================================================

int getSmoothedClass(int current_pred)
{
    pred_history[history_idx] = current_pred;

    history_idx =
        (history_idx + 1) % DEBOUNCE_HISTORY_LEN;

    int votes[PDM_CLASS_COUNT] = {0};

    for (int i = 0; i < DEBOUNCE_HISTORY_LEN; ++i)
    {
        if (pred_history[i] >= 0 &&
            pred_history[i] < PDM_CLASS_COUNT)
        {
            votes[pred_history[i]]++;
        }
    }

    int best_c = current_pred;
    int max_v = 0;

    for (int c = 0; c < PDM_CLASS_COUNT; ++c)
    {
        if (votes[c] > max_v)
        {
            max_v = votes[c];
            best_c = c;
        }
    }

    return best_c;
}

// ============================================================================
// LED Status
// ============================================================================

void updateClassLed(int raw_class_id, float health_index)
{
    const int class_id = getSmoothedClass(raw_class_id);

    switch (class_id)
    {
        case 0:
            // F1 - Repeat Load Step
            setStatusColor(255, 120, 0);
            break;

        case 1:
            // F2 - Step Load Increase
            setStatusColor(255, 220, 0);
            break;

        case 2:
            // F3 - Current Spike
            setStatusColor(180, 0, 255);
            break;

        case 3:
            // F4 - Undervoltage
            setStatusColor(255, 0, 0);
            break;

        case 4:
            // HEALTHY
            setStatusColor(0, 255, 0);
            break;

        default:
            setStatusColor(0, 0, 255);
            break;
    }
}

// ============================================================================
// Encoder ISR
// ============================================================================

void IRAM_ATTR encoderISR()
{
    const uint32_t now = micros();

    if (g_last_pulse_us == 0)
    {
        g_last_pulse_us = now;
        return;
    }

    const uint32_t dt =
        now - g_last_pulse_us;

    if (dt < ENCODER_DEBOUNCE_US)
        return;

    if (dt >= MIN_VALID_PERIOD_US)
    {
        g_pulse_period_us = dt;
        g_last_pulse_us = now;
    }
}

// ============================================================================
// RPM
// ============================================================================

float readInstantaneousRpm()
{
    uint32_t period_us;
    uint32_t last_time;

    noInterrupts();

    period_us = g_pulse_period_us;
    last_time = g_last_pulse_us;

    interrupts();

    if (
        last_time == 0 ||
        (micros() - last_time > 2000000)
    )
    {
        return 0.0f;
    }

    if (period_us >= MIN_VALID_PERIOD_US)
    {
        return
            60000000.0f /
            (float)period_us;
    }

    return 0.0f;
}

// ============================================================================
// Static Working Buffers
// ============================================================================

static float s_ax[BUFFER_SIZE];
static float s_ay[BUFFER_SIZE];
static float s_az[BUFFER_SIZE];
static float s_acs[BUFFER_SIZE];

static float s_rpm[BUFFER_SIZE];

static float s_valid_rpm[BUFFER_SIZE];
static float s_valid_t[BUFFER_SIZE];
static float s_valid_rpm_sorted[BUFFER_SIZE];

// ============================================================================
// Insertion Sort
// ============================================================================

void insertionSort(float arr[], int n)
{
    for (int i = 1; i < n; ++i)
    {
        const float key = arr[i];

        int j = i - 1;

        while (
            j >= 0 &&
            arr[j] > key
        )
        {
            arr[j + 1] = arr[j];
            --j;
        }

        arr[j + 1] = key;
    }
}

// ============================================================================
// Process Rolling Window + AI Prediction
// ============================================================================

void processRollingWindow()
{
    float az_sum = 0.0f;
    float ay_sum = 0.0f;
    float ax_sum = 0.0f;
    float acs_sum = 0.0f;

    float acs_min = 1e6f;
    float acs_max = -1e6f;

    // ------------------------------------------------------------------------
    // Copy circular buffer into processing buffers
    // ------------------------------------------------------------------------

    for (int i = 0; i < BUFFER_SIZE; ++i)
    {
        const int idx =
            (write_index + i) % BUFFER_SIZE;

        s_ax[i] = ax_ring[idx];
        s_ay[i] = ay_ring[idx];
        s_az[i] = az_ring[idx];
        s_acs[i] = acs_ring[idx];
        s_rpm[i] = rpm_ring[idx];

        ax_sum += s_ax[i];
        ay_sum += s_ay[i];
        az_sum += s_az[i];
        acs_sum += s_acs[i];

        acs_min =
            min(acs_min, s_acs[i]);

        acs_max =
            max(acs_max, s_acs[i]);
    }

    // ------------------------------------------------------------------------
    // Mean values
    // ------------------------------------------------------------------------

    const float ax_mean =
        ax_sum / (float)BUFFER_SIZE;

    const float ay_mean =
        ay_sum / (float)BUFFER_SIZE;

    const float az_mean =
        az_sum / (float)BUFFER_SIZE;

    const float acs_mean =
        acs_sum / (float)BUFFER_SIZE;

    const float acs_p2p =
        acs_max - acs_min;

    // ------------------------------------------------------------------------
    // ACS712 current slope
    // ------------------------------------------------------------------------

    float num_acs = 0.0f;

    for (int i = 0; i < BUFFER_SIZE; ++i)
    {
        const float dt =
            ((float)i / 200.0f) - 0.4975f;

        num_acs +=
            dt *
            (s_acs[i] - acs_mean);
    }

    const float acs_dI_dt_slope =
        num_acs / 16.66625f;

    // ------------------------------------------------------------------------
    // Dynamic acceleration features
    // ------------------------------------------------------------------------

    float ay_sq_sum = 0.0f;
    float az_sq_sum = 0.0f;
    float ax_sq_sum = 0.0f;

    float ay_min = 1e6f;
    float ay_max = -1e6f;

    float az_min = 1e6f;
    float az_max = -1e6f;

    float ax_peak = 0.0f;

    for (int i = 0; i < BUFFER_SIZE; ++i)
    {
        const float ax_d =
            s_ax[i] - ax_mean;

        const float ay_d =
            s_ay[i] - ay_mean;

        const float az_d =
            s_az[i] - az_mean;

        ax_sq_sum +=
            ax_d * ax_d;

        ax_peak =
            max(ax_peak, fabsf(ax_d));

        ay_sq_sum +=
            ay_d * ay_d;

        ay_min =
            min(ay_min, ay_d);

        ay_max =
            max(ay_max, ay_d);

        az_sq_sum +=
            az_d * az_d;

        az_min =
            min(az_min, az_d);

        az_max =
            max(az_max, az_d);
    }

    const float ax_rms =
        sqrtf(
            ax_sq_sum /
            (float)BUFFER_SIZE
        );

    const float ax_crest =
        ax_rms > 1e-6f
        ? ax_peak / ax_rms
        : 0.0f;

    const float ay_rms =
        sqrtf(
            ay_sq_sum /
            (float)BUFFER_SIZE
        );

    const float ay_p2p =
        ay_max - ay_min;

    const float az_std =
        sqrtf(
            az_sq_sum /
            (float)BUFFER_SIZE
        );

    // ------------------------------------------------------------------------
    // RPM validation
    // ------------------------------------------------------------------------

    int valid_count = 0;

    float rpm_sum = 0.0f;
    float t_sum = 0.0f;

    for (int i = 0; i < BUFFER_SIZE; ++i)
    {
        if (
            s_rpm[i] > 0.0f &&
            s_rpm[i] <= RPM_HARD_MAX
        )
        {
            const float t_sec =
                (float)i / 200.0f;

            s_valid_rpm[valid_count] =
                s_rpm[i];

            s_valid_t[valid_count] =
                t_sec;

            s_valid_rpm_sorted[valid_count] =
                s_rpm[i];

            rpm_sum += s_rpm[i];
            t_sum += t_sec;

            valid_count++;
        }
    }

    if (
        valid_count <
        BUFFER_SIZE / 3
    )
    {
        setStatusColor(0, 0, 255);

        return;
    }

    // ------------------------------------------------------------------------
    // RPM slope
    // ------------------------------------------------------------------------

    const float t_mean_rpm =
        t_sum / (float)valid_count;

    const float rpm_mean_val =
        rpm_sum / (float)valid_count;

    float num_rpm = 0.0f;
    float den_rpm = 0.0f;

    for (int i = 0; i < valid_count; ++i)
    {
        const float dt =
            s_valid_t[i] -
            t_mean_rpm;

        num_rpm +=
            dt *
            (s_valid_rpm[i] -
             rpm_mean_val);

        den_rpm +=
            dt * dt;
    }

    const float rpm_slope_rpm_per_s =
        den_rpm > 1e-6f
        ? num_rpm / den_rpm
        : 0.0f;

    // ------------------------------------------------------------------------
    // RPM statistics
    // ------------------------------------------------------------------------

    insertionSort(
        s_valid_rpm_sorted,
        valid_count
    );

    const float rpm_min =
        s_valid_rpm_sorted[0];

    const float rpm_max =
        s_valid_rpm_sorted[
            valid_count - 1
        ];

    const float rpm_p2p =
        rpm_max - rpm_min;

    const float rpm_median =
        valid_count % 2
        ?
        s_valid_rpm_sorted[
            valid_count / 2
        ]
        :
        (
            s_valid_rpm_sorted[
                valid_count / 2 - 1
            ]
            +
            s_valid_rpm_sorted[
                valid_count / 2
            ]
        ) * 0.5f;

    // ------------------------------------------------------------------------
    // Order 2X Energy
    // ------------------------------------------------------------------------

    const float f_2x =
        (rpm_median / 60.0f) * 2.0f;

    float order_2x_energy = 0.0f;

    if (
        f_2x > 0.0f &&
        f_2x < 100.0f
    )
    {
        float real_sum = 0.0f;
        float imag_sum = 0.0f;

        const float omega =
            2.0f *
            (float)M_PI *
            f_2x /
            200.0f;

        for (int i = 0;
             i < BUFFER_SIZE;
             ++i)
        {
            const float ax_d =
                s_ax[i] - ax_mean;

            const float ay_d =
                s_ay[i] - ay_mean;

            const float az_d =
                s_az[i] - az_mean;

            const float mag_d =
                sqrtf(
                    ax_d * ax_d +
                    ay_d * ay_d +
                    az_d * az_d
                );

            const float hanning =
                0.5f *
                (
                    1.0f -
                    cosf(
                        2.0f *
                        (float)M_PI *
                        i /
                        (BUFFER_SIZE - 1)
                    )
                );

            real_sum +=
                (mag_d * hanning) *
                cosf(omega * i);

            imag_sum -=
                (mag_d * hanning) *
                sinf(omega * i);
        }

        order_2x_energy =
            real_sum * real_sum +
            imag_sum * imag_sum;
    }

    // ------------------------------------------------------------------------
    // EXACT 12-feature vector
    // ------------------------------------------------------------------------

    const float features[PDM_FEATURE_COUNT] =
    {
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

        az_std
    };

    // ------------------------------------------------------------------------
    // AI INFERENCE
    // ------------------------------------------------------------------------

    float confidence = 0.0f;
    float health_index = 100.0f;

    const int pred_class =
        pdmPredict(
            features,
            &confidence,
            &health_index
        );

    // ------------------------------------------------------------------------
    // Smooth class
    // ------------------------------------------------------------------------

    const int smoothed_class =
        getSmoothedClass(pred_class);

    updateClassLed(
        pred_class,
        health_index
    );

    // ------------------------------------------------------------------------
    // Store latest prediction for dashboard
    // ------------------------------------------------------------------------

    g_prediction_class =
        smoothed_class;

    g_health_index =
        health_index;

    g_confidence =
        confidence * 100.0f;

    g_rpm =
        rpm_median;

    g_rpm_slope =
        rpm_slope_rpm_per_s;

    g_current_slope =
        acs_dI_dt_slope;

    g_prediction_timestamp =
        millis();

    g_prediction_available =
        true;

    // ------------------------------------------------------------------------
    // Serial JSON
    // ------------------------------------------------------------------------

    Serial.printf(
        "{\"ts\":%lu,"
        "\"pred\":\"%s\","
        "\"health\":%.1f,"
        "\"conf\":%.1f,"
        "\"rpm\":%.1f,"
        "\"slope\":%.1f,"
        "\"dI_dt\":%.1f}\n",

        millis(),

        PDM_LABELS[
            smoothed_class
        ],

        health_index,

        confidence * 100.0f,

        rpm_median,

        rpm_slope_rpm_per_s,

        acs_dI_dt_slope
    );
}

// ============================================================================
// Wi-Fi
// ============================================================================

void connectToWiFi()
{
    Serial.println();
    Serial.println("=================================");
    Serial.println("Connecting to Wi-Fi...");
    Serial.println("=================================");

    WiFi.mode(WIFI_STA);

    WiFi.begin(
        WIFI_SSID,
        WIFI_PASSWORD
    );

    uint32_t startAttempt =
        millis();

    while (
        WiFi.status() != WL_CONNECTED &&
        millis() - startAttempt < 20000
    )
    {
        delay(500);

        Serial.print(".");
    }

    Serial.println();

    if (
        WiFi.status() == WL_CONNECTED
    )
    {
        Serial.println("Wi-Fi connected!");

        Serial.print("SSID: ");
        Serial.println(WiFi.SSID());

        Serial.print("ESP32 IP address: ");
        Serial.println(WiFi.localIP());

        Serial.print("Signal strength: ");
        Serial.print(WiFi.RSSI());
        Serial.println(" dBm");

        Serial.println();
        Serial.println("Open this address on your laptop:");
        Serial.print("http://");
        Serial.println(WiFi.localIP());

        Serial.println();
    }
    else
    {
        Serial.println(
            "WARNING: Wi-Fi connection failed."
        );

        Serial.println(
            "ML will continue running."
        );
    }
}

// ============================================================================
// Dashboard HTML
// ============================================================================

const char DASHBOARD_HTML[] PROGMEM = R"rawliteral(

<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>
ESP32 Predictive Maintenance
</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, Helvetica, sans-serif;
    background: #111827;
    color: #f9fafb;
}

.header {
    background: #1f2937;
    padding: 20px 30px;
    border-bottom: 1px solid #374151;
}

.header h1 {
    margin: 0;
    font-size: 28px;
}

.header p {
    margin: 6px 0 0;
    color: #9ca3af;
}

.container {
    max-width: 1300px;
    margin: auto;
    padding: 25px;
}

.connection {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
}

.dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #ef4444;
}

.dot.connected {
    background: #22c55e;
}

.grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(220px, 1fr));

    gap: 18px;
}

.card {
    background: #1f2937;
    border-radius: 14px;
    padding: 20px;
    border: 1px solid #374151;
}

.card-title {
    color: #9ca3af;
    font-size: 14px;
    margin-bottom: 12px;
}

.value {
    font-size: 32px;
    font-weight: bold;
}

.unit {
    font-size: 15px;
    color: #9ca3af;
}

.status-card {
    margin-top: 20px;
    background: #1f2937;
    border-radius: 14px;
    padding: 25px;
    border: 1px solid #374151;
}

.status {
    font-size: 42px;
    font-weight: bold;
    margin-top: 10px;
}

.status.healthy {
    color: #22c55e;
}

.status.warning {
    color: #facc15;
}

.status.fault {
    color: #ef4444;
}

.status.fault2 {
    color: #c084fc;
}

.health-container {
    margin-top: 20px;
}

.health-bar {
    width: 100%;
    height: 25px;
    background: #374151;
    border-radius: 15px;
    overflow: hidden;
}

.health-fill {
    height: 100%;
    width: 100%;
    transition: width 0.4s ease;
    background: #22c55e;
}

.health-text {
    margin-top: 8px;
    font-size: 18px;
}

.info {
    margin-top: 20px;
    color: #9ca3af;
    font-size: 13px;
}

.footer {
    text-align: center;
    margin-top: 30px;
    color: #6b7280;
}

</style>

</head>

<body>

<div class="header">

<h1>
⚙️ Edge AI Predictive Maintenance
</h1>

<p>
ESP32-S3 Real-Time Motor Condition Monitoring
</p>

</div>

<div class="container">

<div class="connection">

<div id="connectionDot"
     class="dot">
</div>

<span id="connectionText">
Connecting...
</span>

</div>


<div class="grid">

<div class="card">

<div class="card-title">
MOTOR HEALTH
</div>

<div class="value">
<span id="health">
--</span>
<span class="unit">%</span>
</div>

</div>


<div class="card">

<div class="card-title">
PREDICTION CONFIDENCE
</div>

<div class="value">
<span id="confidence">
--</span>
<span class="unit">%</span>
</div>

</div>


<div class="card">

<div class="card-title">
RPM
</div>

<div class="value">
<span id="rpm">
--
</span>

<span class="unit">
RPM
</span>

</div>

</div>


<div class="card">

<div class="card-title">
RPM SLOPE
</div>

<div class="value">

<span id="rpmSlope">
--
</span>

<span class="unit">
RPM/s
</span>

</div>

</div>


<div class="card">

<div class="card-title">
CURRENT dI/dt
</div>

<div class="value">

<span id="currentSlope">
--
</span>

<span class="unit">
ADC/s
</span>

</div>

</div>


<div class="card">

<div class="card-title">
LAST PREDICTION
</div>

<div class="value"
     style="font-size:20px">

<span id="timestamp">
--
</span>

</div>

</div>

</div>


<div class="status-card">

<div class="card-title">
PREDICTED MOTOR CONDITION
</div>

<div id="prediction"
     class="status healthy">

WAITING...

</div>


<div class="health-container">

<div class="card-title">
HEALTH INDEX
</div>

<div class="health-bar">

<div id="healthFill"
     class="health-fill">
</div>

</div>

<div class="health-text">

Health:
<span id="health2">
--
</span>%

</div>

</div>

</div>


<div class="info">

AI inference is performed locally on the ESP32.
The laptop is used only for visualization.

</div>


<div class="footer">

ESP32 Edge AI • Predictive Maintenance Dashboard

</div>

</div>


<script>

function updateDashboard(data)
{

    document.getElementById(
        "health"
    ).textContent =
        Number(data.health).toFixed(1);


    document.getElementById(
        "health2"
    ).textContent =
        Number(data.health).toFixed(1);


    document.getElementById(
        "confidence"
    ).textContent =
        Number(data.conf).toFixed(1);


    document.getElementById(
        "rpm"
    ).textContent =
        Number(data.rpm).toFixed(1);


    document.getElementById(
        "rpmSlope"
    ).textContent =
        Number(data.slope).toFixed(1);


    document.getElementById(
        "currentSlope"
    ).textContent =
        Number(data.dI_dt).toFixed(2);


    document.getElementById(
        "prediction"
    ).textContent =
        data.pred;


    document.getElementById(
        "timestamp"
    ).textContent =
        (Number(data.ts) / 1000).toFixed(1)
        + " s";


    const prediction =
        document.getElementById(
            "prediction"
        );


    prediction.className =
        "status";


    if (data.pred === "HEALTHY")
    {
        prediction.classList.add(
            "healthy"
        );
    }

    else if (
        data.pred === "F1" ||
        data.pred === "F2"
    )
    {
        prediction.classList.add(
            "warning"
        );
    }

    else if (
        data.pred === "F3"
    )
    {
        prediction.classList.add(
            "fault2"
        );
    }

    else
    {
        prediction.classList.add(
            "fault"
        );
    }


    const health =
        Math.max(
            0,
            Math.min(
                100,
                Number(data.health)
            )
        );


    document.getElementById(
        "healthFill"
    ).style.width =
        health + "%";
}


async function getData()
{

    try
    {

        const response =
            await fetch(
                "/api/data",
                {
                    cache: "no-store"
                }
            );


        if (!response.ok)
            throw new Error(
                "HTTP error"
            );


        const data =
            await response.json();


        updateDashboard(data);


        document.getElementById(
            "connectionDot"
        ).classList.add(
            "connected"
        );


        document.getElementById(
            "connectionText"
        ).textContent =
            "ESP32 connected";


    }

    catch (error)
    {

        document.getElementById(
            "connectionDot"
        ).classList.remove(
            "connected"
        );


        document.getElementById(
            "connectionText"
        ).textContent =
            "ESP32 disconnected";

    }

}


setInterval(
    getData,
    500
);


getData();

</script>

</body>

</html>

)rawliteral";

// ============================================================================
// HTTP: Dashboard
// ============================================================================

void handleRoot()
{
    server.send_P(
        200,
        "text/html",
        DASHBOARD_HTML
    );
}

// ============================================================================
// HTTP: JSON API
// ============================================================================

void handleData()
{
    String json;

    json.reserve(512);

    json += "{";

    json += "\"available\":";
    json += g_prediction_available
        ? "true"
        : "false";

    json += ",";

    json += "\"ts\":";
    json += String(
        g_prediction_timestamp
    );

    json += ",";

    json += "\"pred\":\"";

    if (
        g_prediction_class >= 0 &&
        g_prediction_class < PDM_CLASS_COUNT
    )
    {
        json +=
            PDM_LABELS[
                g_prediction_class
            ];
    }
    else
    {
        json += "UNKNOWN";
    }

    json += "\"";

    json += ",";

    json += "\"health\":";
    json += String(
        g_health_index,
        1
    );

    json += ",";

    json += "\"conf\":";
    json += String(
        g_confidence,
        1
    );

    json += ",";

    json += "\"rpm\":";
    json += String(
        g_rpm,
        1
    );

    json += ",";

    json += "\"slope\":";
    json += String(
        g_rpm_slope,
        1
    );

    json += ",";

    json += "\"dI_dt\":";
    json += String(
        g_current_slope,
        2
    );

    json += ",";

    json += "\"temperature\":";
    json += String(
        g_temperature,
        2
    );

    json += "}";

    server.send(
        200,
        "application/json",
        json
    );
}

// ============================================================================
// HTTP: Not Found
// ============================================================================

void handleNotFound()
{
    server.send(
        404,
        "text/plain",
        "404 - Not Found"
    );
}

// ============================================================================
// Start Web Server
// ============================================================================

void startWebServer()
{
    server.on(
        "/",
        HTTP_GET,
        handleRoot
    );

    server.on(
        "/api/data",
        HTTP_GET,
        handleData
    );

    server.onNotFound(
        handleNotFound
    );

    server.begin();

    Serial.println(
        "HTTP dashboard server started."
    );
}

// ============================================================================
// SETUP
// ============================================================================

void setup()
{
    Serial.begin(115200);

    delay(500);

    Serial.println();
    Serial.println(
        "--- DC Motor Enhanced Predictive Maintenance Node ---"
    );

    // ------------------------------------------------------------------------
    // LED
    // ------------------------------------------------------------------------

    statusLed.begin();

    statusLed.clear();

    setStatusColor(
        0,
        0,
        255
    );

    // ------------------------------------------------------------------------
    // I2C
    // ------------------------------------------------------------------------

    Wire.begin(
        I2C_SDA_PIN,
        I2C_SCL_PIN
    );

    if (!mpu.begin())
    {
        Serial.println(
            "ERROR: MPU6050 accelerometer not detected!"
        );

        while (true)
        {
            setStatusColor(
                255,
                0,
                0
            );

            delay(200);

            setStatusColor(
                0,
                0,
                0
            );

            delay(200);
        }
    }

    mpu.setAccelerometerRange(
        MPU6050_RANGE_4_G
    );

    mpu.setFilterBandwidth(
        MPU6050_BAND_94_HZ
    );

    // ------------------------------------------------------------------------
    // ADC
    // ------------------------------------------------------------------------

    analogReadResolution(12);

    analogSetPinAttenuation(
        ACS712_ADC_PIN,
        ADC_11db
    );

    // ------------------------------------------------------------------------
    // Encoder
    // ------------------------------------------------------------------------

    pinMode(
        ENCODER_INDEX_PIN,
        INPUT_PULLUP
    );

    attachInterrupt(
        digitalPinToInterrupt(
            ENCODER_INDEX_PIN
        ),
        encoderISR,
        RISING
    );

    // ------------------------------------------------------------------------
    // ACS712 Zero Calibration
    // ------------------------------------------------------------------------

    Serial.println(
        "Calibrating ACS712 zero-current offset..."
    );

    uint32_t adc_sum = 0;

    for (int i = 0; i < 200; ++i)
    {
        adc_sum +=
            analogRead(
                ACS712_ADC_PIN
            );

        delayMicroseconds(1000);
    }

    acs_zero_offset =
        (float)adc_sum /
        200.0f;

    Serial.printf(
        "ACS712 Zero Calibration Offset: %.1f ADC counts\n",
        acs_zero_offset
    );

    // ------------------------------------------------------------------------
    // Wi-Fi
    // ------------------------------------------------------------------------

    connectToWiFi();

    if (
        WiFi.status() == WL_CONNECTED
    )
    {
        startWebServer();
    }

    // ------------------------------------------------------------------------
    // Ready
    // ------------------------------------------------------------------------

    setStatusColor(
        0,
        255,
        0
    );

    Serial.println(
        "Sampling started @ 200 Hz"
    );

    Serial.println(
        "250 ms rolling inference enabled."
    );
}

// ============================================================================
// LOOP
// ============================================================================

void loop()
{
    // ------------------------------------------------------------------------
    // IMPORTANT:
    // Handle browser requests continuously.
    // This must NOT be placed after the sampling return.
    // ------------------------------------------------------------------------

    if (
        WiFi.status() == WL_CONNECTED
    )
    {
        server.handleClient();
    }

    // ------------------------------------------------------------------------
    // 200 Hz sampling
    // ------------------------------------------------------------------------

    static uint32_t last_sample_us = 0;

    const uint32_t now = micros();

    if (
        now - last_sample_us <
        SAMPLE_PERIOD_US
    )
    {
        return;
    }

    last_sample_us = now;

    // ------------------------------------------------------------------------
    // Read MPU6050
    // ------------------------------------------------------------------------

    sensors_event_t accel;
    sensors_event_t gyro;
    sensors_event_t temp;

    mpu.getEvent(
        &accel,
        &gyro,
        &temp
    );

    g_temperature =
        temp.temperature;

    // ------------------------------------------------------------------------
    // Store sensor values
    // ------------------------------------------------------------------------

    ax_ring[write_index] =
        accel.acceleration.x;

    ay_ring[write_index] =
        accel.acceleration.y;

    az_ring[write_index] =
        accel.acceleration.z;

    acs_ring[write_index] =
        (float)analogRead(
            ACS712_ADC_PIN
        )
        -
        acs_zero_offset;

    rpm_ring[write_index] =
        readInstantaneousRpm();

    // ------------------------------------------------------------------------
    // Advance ring buffer
    // ------------------------------------------------------------------------

    write_index =
        (write_index + 1) %
        BUFFER_SIZE;

    // ------------------------------------------------------------------------
    // Wait for first complete 1-second window
    // ------------------------------------------------------------------------

    if (
        samples_accumulated <
        BUFFER_SIZE
    )
    {
        samples_accumulated++;
    }

    else
    {
        stride_counter++;

        // --------------------------------------------------------------------
        // Inference every 50 samples = 250 ms
        // --------------------------------------------------------------------

        if (
            stride_counter >=
            INFERENCE_STRIDE
        )
        {
            processRollingWindow();

            stride_counter = 0;
        }
    }
}
