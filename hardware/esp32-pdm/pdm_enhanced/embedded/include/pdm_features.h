// ============================================================================
// Enhanced Predictive Maintenance: On-device feature extraction
//
// Mirrors pdm_enhanced/data_processing/feature_extractor.py:
//   clean_rpm, compute_rpm_features, compute_current_and_coupling_features
//   and the vibration statistics in extract_window_features.
// Keep these two files in sync. The host parity test
// (pdm_enhanced/tests/test_firmware_feature_parity.py) compiles this header
// and compares its output with the Python pipeline on real recordings.
//
// No Arduino dependencies, so it builds on a host compiler.
// Avoid NaN sentinels: the firmware is built with -ffast-math, which may
// optimise NaN checks away. Validity is tracked with explicit bool flags.
// ============================================================================

#pragma once
#ifndef PDM_FEATURES_H
#define PDM_FEATURES_H

#include <cmath>

namespace pdm {

constexpr int WINDOW_SAMPLES = 200;        // 1.0 s at 200 Hz
constexpr float SAMPLE_RATE_HZ = 200.0f;
constexpr float RPM_HARD_MAX = 5000.0f;
constexpr float RPM_JUMP_LIMIT = 1000.0f;
constexpr int RPM_MEDIAN_WINDOW = 5;

// Deployment guard, not part of the Python training pipeline: a window is only
// classified when at least one third of its RPM samples are valid.
constexpr int MIN_VALID_RPM = WINDOW_SAMPLES / 3;

// Output order. Must match PDM_FEATURE_NAMES in pdm_model.h.
enum FeatureIndex {
  F_RPM_MIN = 0,
  F_RPM_MEDIAN,
  F_RPM_SLOPE,
  F_RPM_P2P,
  F_ACS_DIDT,
  F_ACS_P2P,
  F_AZ_MEAN,
  F_AY_RMS,
  F_AY_P2P,
  F_AX_CREST,
  F_AZ_STD,
  F_COUNT
};

// Insertion sort in place. Small arrays only (window length).
inline void insertionSortF(float arr[], int n) {
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

// Python clean_rpm():
//   1. keep samples with 0 < rpm <= RPM_HARD_MAX
//   2. drop samples further than RPM_JUMP_LIMIT from the running median
//      (5-sample centred window over the bounded samples)
//   3. drop both samples of any adjacent bounded pair that jumps by more
//      than RPM_JUMP_LIMIT
// Writes one flag per sample and returns the number of valid samples.
inline int cleanRpm(const float raw[], int n, bool valid[]) {
  bool bounded[WINDOW_SAMPLES];
  for (int i = 0; i < n; ++i) {
    bounded[i] = (raw[i] > 0.0f) && (raw[i] <= RPM_HARD_MAX);
    valid[i] = bounded[i];
  }

  // Step 2: median filter over bounded neighbours (pandas min_periods=1 behaviour)
  const int half = RPM_MEDIAN_WINDOW / 2;
  for (int i = 0; i < n; ++i) {
    if (!valid[i]) continue;
    float nb[RPM_MEDIAN_WINDOW];
    int m = 0;
    for (int j = i - half; j <= i + half; ++j) {
      if (j >= 0 && j < n && bounded[j]) nb[m++] = raw[j];
    }
    if (m == 0) continue;  // unreachable: sample i is its own neighbour
    insertionSortF(nb, m);
    const float median = (m % 2) ? nb[m / 2] : 0.5f * (nb[m / 2 - 1] + nb[m / 2]);
    if (std::fabs(raw[i] - median) > RPM_JUMP_LIMIT) valid[i] = false;
  }

  // Step 3: adjacent jump check on bounded samples
  for (int i = 0; i + 1 < n; ++i) {
    if (bounded[i] && bounded[i + 1] && std::fabs(raw[i + 1] - raw[i]) > RPM_JUMP_LIMIT) {
      valid[i] = false;
      valid[i + 1] = false;
    }
  }

  int count = 0;
  for (int i = 0; i < n; ++i) count += valid[i] ? 1 : 0;
  return count;
}

// Compute the 11 deployed features for one 1-second window, in the order of FeatureIndex.
// Inputs are raw sensor samples (oldest first). Returns false when the window
// has fewer than MIN_VALID_RPM valid RPM samples, in which case out[] is not written.
inline bool extractFeatures(const float ax[], const float ay[], const float az[],
                            const float acs[], const float rpm_raw[],
                            float out[F_COUNT]) {
  constexpr int n = WINDOW_SAMPLES;
  constexpr float fs = SAMPLE_RATE_HZ;

  // ---- RPM ----------------------------------------------------------------
  bool rpm_valid[n];
  const int nvalid = cleanRpm(rpm_raw, n, rpm_valid);
  if (nvalid < MIN_VALID_RPM) return false;

  static float sorted[n];
  float rpm_sum = 0.0f, t_sum = 0.0f;
  int k = 0;
  for (int i = 0; i < n; ++i) {
    if (!rpm_valid[i]) continue;
    sorted[k++] = rpm_raw[i];
    rpm_sum += rpm_raw[i];
    t_sum += (float)i / fs;
  }
  const float rpm_mean = rpm_sum / (float)k;
  const float t_mean = t_sum / (float)k;

  // Least-squares slope of RPM versus time over the valid samples (np.polyfit degree 1)
  float num = 0.0f, den = 0.0f;
  for (int i = 0; i < n; ++i) {
    if (!rpm_valid[i]) continue;
    const float dt = (float)i / fs - t_mean;
    num += dt * (rpm_raw[i] - rpm_mean);
    den += dt * dt;
  }
  const float rpm_slope = den > 1e-6f ? num / den : 0.0f;

  insertionSortF(sorted, k);
  const float rpm_min = sorted[0];
  const float rpm_max = sorted[k - 1];
  const float rpm_median = (k % 2) ? sorted[k / 2] : 0.5f * (sorted[k / 2 - 1] + sorted[k / 2]);

  out[F_RPM_MIN] = rpm_min;
  out[F_RPM_MEDIAN] = rpm_median;
  out[F_RPM_SLOPE] = rpm_slope;
  out[F_RPM_P2P] = rpm_max - rpm_min;

  // ---- Current (ACS712 ADC counts; slope and p2p are offset-invariant) ----
  float acs_sum = 0.0f, acs_min = acs[0], acs_max = acs[0];
  for (int i = 0; i < n; ++i) {
    acs_sum += acs[i];
    if (acs[i] < acs_min) acs_min = acs[i];
    if (acs[i] > acs_max) acs_max = acs[i];
  }
  const float acs_mean = acs_sum / (float)n;

  // Slope of acs versus t = i/fs. Sum of squared centred time offsets is n(n^2-1)/12 / fs^2.
  const float t_centre = (float)(n - 1) / (2.0f * fs);
  float acs_num = 0.0f;
  for (int i = 0; i < n; ++i) {
    acs_num += ((float)i / fs - t_centre) * (acs[i] - acs_mean);
  }
  const float acs_sxx = (float)n * ((float)n * (float)n - 1.0f) / 12.0f / (fs * fs);
  out[F_ACS_DIDT] = acs_num / acs_sxx;
  out[F_ACS_P2P] = acs_max - acs_min;

  // ---- Vibration (mean-subtracted dynamic signals) -------------------------
  float ax_m = 0.0f, ay_m = 0.0f, az_m = 0.0f;
  for (int i = 0; i < n; ++i) {
    ax_m += ax[i];
    ay_m += ay[i];
    az_m += az[i];
  }
  ax_m /= (float)n;
  ay_m /= (float)n;
  az_m /= (float)n;

  float ax_sq = 0.0f, ax_peak = 0.0f;
  float ay_sq = 0.0f, ay_min = 1e30f, ay_max = -1e30f;
  float az_sq = 0.0f;
  for (int i = 0; i < n; ++i) {
    const float dx = ax[i] - ax_m;
    const float dy = ay[i] - ay_m;
    const float dz = az[i] - az_m;
    ax_sq += dx * dx;
    const float adx = std::fabs(dx);
    if (adx > ax_peak) ax_peak = adx;
    ay_sq += dy * dy;
    if (dy < ay_min) ay_min = dy;
    if (dy > ay_max) ay_max = dy;
    az_sq += dz * dz;
  }

  const float ax_rms = std::sqrt(ax_sq / (float)n);
  out[F_AX_CREST] = ax_rms > 1e-9f ? ax_peak / ax_rms : 0.0f;
  out[F_AY_RMS] = std::sqrt(ay_sq / (float)n);
  out[F_AY_P2P] = ay_max - ay_min;
  out[F_AZ_MEAN] = az_m;
  out[F_AZ_STD] = std::sqrt(az_sq / (float)n);

  return true;
}

}  // namespace pdm

#endif  // PDM_FEATURES_H
