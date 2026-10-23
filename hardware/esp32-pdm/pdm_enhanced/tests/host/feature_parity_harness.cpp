// Host harness for firmware feature parity.
//
// Reads one window per line from a CSV file. Each line holds 5 * 200 values:
// ax[200], ay[200], az[200], acs[200], rpm[200] (oldest sample first).
// For each window it prints one line: "<ok>,<f0>,...,<f10>" using the exact
// on-device feature code in embedded/include/pdm_features.h.
//
// Built and run by pdm_enhanced/tests/test_firmware_feature_parity.py.

#include <cstdio>
#include "pdm_features.h"

int main(int argc, char **argv) {
  if (argc != 2) {
    std::fprintf(stderr, "usage: %s windows.csv\n", argv[0]);
    return 2;
  }
  FILE *fp = std::fopen(argv[1], "r");
  if (!fp) {
    std::fprintf(stderr, "cannot open %s\n", argv[1]);
    return 2;
  }

  constexpr int N = pdm::WINDOW_SAMPLES;
  static float ax[N], ay[N], az[N], acs[N], rpm[N];
  float out[pdm::F_COUNT];

  while (true) {
    bool row_ok = true;
    float *channels[5] = {ax, ay, az, acs, rpm};
    for (int c = 0; c < 5 && row_ok; ++c) {
      for (int i = 0; i < N; ++i) {
        if (std::fscanf(fp, "%f%*[,\n]", &channels[c][i]) != 1) {
          row_ok = false;
          break;
        }
      }
    }
    if (!row_ok) break;

    const bool ok = pdm::extractFeatures(ax, ay, az, acs, rpm, out);
    std::printf("%d", ok ? 1 : 0);
    for (int f = 0; f < pdm::F_COUNT; ++f) {
      std::printf(",%.9g", ok ? out[f] : 0.0f);
    }
    std::printf("\n");
  }
  std::fclose(fp);
  return 0;
}
