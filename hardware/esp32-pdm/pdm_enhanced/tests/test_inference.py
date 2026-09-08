"""Integration tests for PDM Enhanced inference engine."""

import unittest
from pathlib import Path
import joblib
import pandas as pd
from pdm_enhanced.inference.predict_motor import predict_stream
from pdm_enhanced.models.anomaly_detector import MotorAnomalyDetector

ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT_DIR / "models" / "saved_models" / "pdm_fault_model.pkl"
ANOMALY_PATH = ROOT_DIR / "models" / "saved_models" / "anomaly_detector.pkl"
WORKSPACE_ROOT = ROOT_DIR.parent
SAMPLE_HEALTHY = WORKSPACE_ROOT / "log_file" / "29_08_26" / "healthy_cc_01A_1.csv"
SAMPLE_F1 = WORKSPACE_ROOT / "log_file" / "29_08_26" / "F1_repeat_cc_0.4_0.8A_1.csv"
SAMPLE_F4 = WORKSPACE_ROOT / "log_file" / "29_08_26" / "F4_UV_cc_1A_9V_12V_1.csv"


class TestInferencePipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.artifact = joblib.load(MODEL_PATH)
        cls.detector = MotorAnomalyDetector.load(ANOMALY_PATH)

    def test_healthy_file_inference(self):
        if not SAMPLE_HEALTHY.exists():
            self.skipTest(f"Sample file not found: {SAMPLE_HEALTHY}")

        df_raw = pd.read_csv(SAMPLE_HEALTHY)
        results_df, summary = predict_stream(
            df_raw=df_raw,
            model_artifact=self.artifact,
            anomaly_detector=self.detector,
            hop_samples=100,
        )

        self.assertGreater(len(results_df), 0)
        self.assertEqual(summary["consensus_prediction"], "HEALTHY")
        self.assertGreaterEqual(summary["mean_health_index"], 70.0)

    def test_f4_undervoltage_inference(self):
        if not SAMPLE_F4.exists():
            self.skipTest(f"Sample file not found: {SAMPLE_F4}")

        df_raw = pd.read_csv(SAMPLE_F4)
        results_df, summary = predict_stream(
            df_raw=df_raw,
            model_artifact=self.artifact,
            anomaly_detector=self.detector,
            hop_samples=50,
        )

        self.assertGreater(len(results_df), 0)
        # F4 undervoltage windows should be detected in the recording
        f4_predictions = (results_df["prediction"] == "F4").sum()
        self.assertGreater(f4_predictions, 0)


if __name__ == "__main__":
    unittest.main()
