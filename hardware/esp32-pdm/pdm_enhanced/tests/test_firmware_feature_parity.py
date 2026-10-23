"""Feature-level parity between the on-device C++ code and the Python pipeline.

The test compiles embedded/include/pdm_features.h with the same optimisation flags as the
firmware (-O3 -ffast-math), runs it on sliding 1-second windows from every raw recording,
and compares the 11 deployed features with feature_extractor.extract_window_features.

Expected behaviour:
  * windows with >= MIN_VALID_RPM (66) valid RPM samples: C++ returns ok and every feature matches
  * windows with fewer valid samples: C++ returns not-ok (deployment guard). Python would still
    produce values for 2..66 valid samples, so these windows are counted, not compared.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import numpy as np

from pdm_enhanced.data_processing.dataset_builder import identify_continuous_segments
from pdm_enhanced.data_processing.feature_extractor import (
    FS,
    WINDOW_SAMPLES,
    clean_rpm,
    extract_window_features,
)

ROOT_DIR = Path(__file__).resolve().parent.parent            # pdm_enhanced/
REPO_HW_DIR = ROOT_DIR.parent                                 # hardware/esp32-pdm/
RAW_DIR = REPO_HW_DIR / "log_file" / "29_08_26"
HARNESS_SRC = ROOT_DIR / "tests" / "host" / "feature_parity_harness.cpp"
INCLUDE_DIR = ROOT_DIR / "embedded" / "include"
HOP_SAMPLES = 50                                              # 250 ms, as on device
MIN_VALID_RPM = WINDOW_SAMPLES // 3                           # on-device guard

DEPLOYED_FEATURES = [
    "rpm_min", "rpm_median", "rpm_slope_rpm_per_s", "rpm_p2p",
    "acs_dI_dt_slope", "acs_p2p", "az_mean", "ay_rms",
    "ay_p2p", "ax_crest", "az_std",
]


def _build_harness(workdir: Path) -> Path:
    binary = workdir / "feature_parity_harness"
    cmd = [
        "g++", "-std=c++17", "-O3", "-ffast-math", "-Wall", "-Wextra", "-Werror",
        f"-I{INCLUDE_DIR}", str(HARNESS_SRC), "-o", str(binary),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return binary


def _collect_windows(raw_files: list[Path]):
    """Yield (file, window arrays, python features, valid-RPM count) like predict_stream does."""
    import pandas as pd

    for path in raw_files:
        df = pd.read_csv(path)
        for seg_start, seg_end in identify_continuous_segments(df["timestamp_ms"].to_numpy()):
            seg = df.iloc[seg_start:seg_end].reset_index(drop=True)
            for start in range(0, len(seg) - WINDOW_SAMPLES + 1, HOP_SAMPLES):
                w = seg.iloc[start:start + WINDOW_SAMPLES]
                arrays = {c: w[c].to_numpy(dtype=float) for c in ("ax", "ay", "az", "acs_adc", "rpm")}
                feats = extract_window_features(
                    ax=arrays["ax"], ay=arrays["ay"], az=arrays["az"],
                    acs_adc=arrays["acs_adc"], rpm_raw=arrays["rpm"], fs=FS,
                )
                n_valid = int(np.isfinite(clean_rpm(arrays["rpm"])).sum())
                yield path.name, arrays, feats, n_valid


class TestFirmwareFeatureParity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if shutil.which("g++") is None:
            raise unittest.SkipTest("g++ not available; cannot build the host harness")
        if not RAW_DIR.is_dir():
            raise unittest.SkipTest(f"raw recordings not found: {RAW_DIR}")

        cls._tmp = tempfile.TemporaryDirectory()
        workdir = Path(cls._tmp.name)
        cls.binary = _build_harness(workdir)

        raw_files = sorted(RAW_DIR.glob("*.csv"))
        windows = list(_collect_windows(raw_files))
        cls.n_files = len(raw_files)
        cls.n_windows = len(windows)

        # Write one CSV row per window: ax | ay | az | acs | rpm (200 values each)
        csv_path = workdir / "windows.csv"
        with csv_path.open("w") as fh:
            for _, arrays, _, _ in windows:
                row = np.concatenate([arrays[c] for c in ("ax", "ay", "az", "acs_adc", "rpm")])
                fh.write(",".join(f"{v:.9g}" for v in row) + "\n")

        proc = subprocess.run([str(cls.binary), str(csv_path)], check=True, capture_output=True, text=True)
        cls.cpp_rows = [line.split(",") for line in proc.stdout.strip().splitlines()]
        cls.windows = windows
        assert len(cls.cpp_rows) == len(windows), "harness row count does not match window count"

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "_tmp"):
            cls._tmp.cleanup()

    def test_feature_parity_on_recordings(self):
        compared = 0
        guard_skipped = 0
        insufficient = 0
        mismatches = []
        max_rel_err = {f: 0.0 for f in DEPLOYED_FEATURES}
        max_abs_err = {f: 0.0 for f in DEPLOYED_FEATURES}

        for idx, ((fname, _, py, n_valid), row) in enumerate(zip(self.windows, self.cpp_rows)):
            cpp_ok = row[0] == "1"
            cpp_vals = np.array([float(v) for v in row[1:]])

            if n_valid >= MIN_VALID_RPM:
                self.assertTrue(cpp_ok, f"window {idx} ({fname}): C++ rejected a window with {n_valid} valid RPM")
                py_vals = np.array([py[f] for f in DEPLOYED_FEATURES])
                self.assertTrue(np.all(np.isfinite(py_vals)), f"window {idx} ({fname}): Python NaN")
                for f_name, c, p in zip(DEPLOYED_FEATURES, cpp_vals, py_vals):
                    scale = max(abs(p), 1e-6)
                    rel = abs(c - p) / scale
                    max_rel_err[f_name] = max(max_rel_err[f_name], rel)
                    max_abs_err[f_name] = max(max_abs_err[f_name], abs(c - p))
                    if not np.isclose(c, p, rtol=1e-3, atol=1e-4):
                        mismatches.append((idx, fname, f_name, float(c), float(p)))
                compared += 1
            else:
                self.assertFalse(cpp_ok, f"window {idx} ({fname}): C++ accepted a window with {n_valid} valid RPM")
                if n_valid >= 2:
                    guard_skipped += 1
                else:
                    insufficient += 1

        print(f"\nFiles: {self.n_files}, windows: {self.n_windows}")
        print(f"Compared: {compared}, guard-rejected (2..{MIN_VALID_RPM - 1} valid RPM): {guard_skipped}, "
              f"insufficient (<2 valid RPM): {insufficient}")
        print("Max absolute / relative error per feature (relative is inflated near zero):")
        for f_name in DEPLOYED_FEATURES:
            print(f"  {f_name:<22} abs {max_abs_err[f_name]:.2e}   rel {max_rel_err[f_name]:.2e}")

        self.assertGreater(compared, 0)
        self.assertEqual(mismatches, [], f"first mismatches: {mismatches[:5]}")


class TestFirmwareRpmRules(unittest.TestCase):
    """Synthetic windows that check the RPM rules directly (no recordings needed)."""

    @classmethod
    def setUpClass(cls):
        if shutil.which("g++") is None:
            raise unittest.SkipTest("g++ not available; cannot build the host harness")
        cls._tmp = tempfile.TemporaryDirectory()
        cls.binary = _build_harness(Path(cls._tmp.name))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def _run(self, rpm: np.ndarray) -> list[str]:
        zeros = np.zeros(WINDOW_SAMPLES)
        row = np.concatenate([zeros + 0.1, zeros + 0.2, zeros + 9.8, zeros + 500.0, rpm])
        csv_path = Path(self._tmp_dir) / "synthetic.csv"
        csv_path.write_text(",".join(f"{v:.9g}" for v in row) + "\n")
        proc = subprocess.run([str(self.binary), str(csv_path)], check=True, capture_output=True, text=True)
        return proc.stdout.strip().split(",")

    def setUp(self):
        self._scratch = tempfile.TemporaryDirectory()
        self._tmp_dir = self._scratch.name

    def tearDown(self):
        self._scratch.cleanup()

    def test_single_jump_spike_is_removed(self):
        # 2800 RPM with one 4900 RPM sample. The median step and the jump step both
        # reject it, so the RPM range collapses to zero (the raw data would give p2p = 2100)
        rpm = np.full(WINDOW_SAMPLES, 2800.0)
        rpm[100] = 4900.0
        out = self._run(rpm)
        self.assertEqual(out[0], "1")
        feats = dict(zip(DEPLOYED_FEATURES, map(float, out[1:])))
        self.assertAlmostEqual(feats["rpm_min"], 2800.0, places=2)
        self.assertAlmostEqual(feats["rpm_median"], 2800.0, places=2)
        self.assertAlmostEqual(feats["rpm_p2p"], 0.0, places=2)

    def test_window_with_too_few_valid_rpm_is_rejected(self):
        # 60 valid samples is below the one-third guard (MIN_VALID_RPM = 66); the window must not be classified
        rpm = np.zeros(WINDOW_SAMPLES)
        rpm[:60] = 2800.0
        out = self._run(rpm)
        self.assertEqual(out[0], "0")

    def test_window_at_guard_threshold_is_accepted(self):
        rpm = np.zeros(WINDOW_SAMPLES)
        rpm[:MIN_VALID_RPM] = 2800.0
        out = self._run(rpm)
        self.assertEqual(out[0], "1")


if __name__ == "__main__":
    unittest.main()
