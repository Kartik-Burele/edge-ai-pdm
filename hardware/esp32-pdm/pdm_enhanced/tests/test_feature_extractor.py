"""Unit tests for signal processing and feature extraction modules."""

import unittest
import numpy as np
from pdm_enhanced.data_processing.feature_extractor import (
    clean_rpm,
    rms,
    peak_to_peak,
    crest_factor,
    signal_skewness,
    signal_kurtosis,
    spectral_and_order_features,
    compute_current_and_coupling_features,
    extract_window_features,
)


class TestFeatureExtractor(unittest.TestCase):

    def test_clean_rpm_bounds_and_jumps(self):
        raw = np.array([2800.0, 2810.0, -50.0, 6500.0, 2805.0, 4500.0, 2810.0])
        cleaned = clean_rpm(raw)
        self.assertEqual(len(cleaned), len(raw))
        self.assertTrue(np.isnan(cleaned[2]))  # Negative bound
        self.assertTrue(np.isnan(cleaned[3]))  # Hard max bound
        self.assertTrue(np.isnan(cleaned[5]))  # Jump limit
        self.assertAlmostEqual(cleaned[0], 2800.0)
        self.assertAlmostEqual(cleaned[1], 2810.0)

    def test_statistical_metrics(self):
        sig = np.array([-2.0, 0.0, 2.0])
        self.assertAlmostEqual(peak_to_peak(sig), 4.0)
        self.assertAlmostEqual(rms(sig), np.sqrt(8.0 / 3.0), places=4)
        self.assertAlmostEqual(signal_skewness(sig), 0.0, places=4)

        # Sine wave crest factor should be ~ sqrt(2) = 1.4142
        t = np.linspace(0, 1, 200)
        sine = np.sin(2 * np.pi * 10 * t)
        self.assertAlmostEqual(crest_factor(sine), np.sqrt(2), places=1)

    def test_spectral_and_order_tracking(self):
        fs = 200
        t = np.arange(200) / fs
        # 40 Hz rotation (2400 RPM), with 1X and 2X harmonics
        signal = 2.0 * np.sin(2 * np.pi * 40 * t) + 1.0 * np.sin(2 * np.pi * 80 * t)
        spec = spectral_and_order_features(signal, rpm_mean=2400.0, fs=fs)

        self.assertAlmostEqual(spec["dominant_frequency_Hz"], 40.0, delta=2.0)
        self.assertGreater(spec["order_1x_energy"], 0.0)
        self.assertGreater(spec["order_2x_energy"], 0.0)
        self.assertGreater(spec["spectral_energy"], 0.0)

    def test_current_coupling_features(self):
        acs = np.linspace(100.0, 200.0, 200)
        elec = compute_current_and_coupling_features(acs, rpm_mean=2800.0, fs=200)
        self.assertAlmostEqual(elec["acs_mean"], 150.0, delta=1.0)
        self.assertGreater(elec["acs_dI_dt_slope"], 0.0)
        self.assertGreater(elec["rpm_to_current_ratio"], 0.0)

    def test_full_window_extraction(self):
        n = 200
        ax = np.random.normal(0, 0.1, n)
        ay = np.random.normal(0, 0.1, n)
        az = np.random.normal(9.8, 0.1, n)
        acs = np.random.normal(500, 10, n)
        rpm = np.random.normal(2850, 10, n)

        feats = extract_window_features(ax, ay, az, acs, rpm, fs=200)
        self.assertIn("az_mean", feats)
        self.assertIn("rpm_median", feats)
        self.assertIn("order_1x_energy", feats)
        self.assertIn("rpm_to_current_ratio", feats)
        self.assertAlmostEqual(feats["az_mean"], 9.8, delta=0.2)


if __name__ == "__main__":
    unittest.main()
