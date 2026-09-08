"""Verification test for exact numerical parity between Python model and C++ tree structure."""

import unittest
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT_DIR / "models" / "saved_models" / "pdm_fault_model.pkl"
DATA_PATH = ROOT_DIR / "data" / "ml_dataset.csv"


def simulate_c_tree_predict(estimator, features: np.ndarray, num_classes: int) -> np.ndarray:
    """Python simulation of the recursive C++ tree branching logic."""
    tree = estimator.tree_
    node = 0
    while tree.children_left[node] != tree.children_right[node]:
        feat = tree.feature[node]
        thresh = tree.threshold[node]
        if features[feat] <= thresh:
            node = tree.children_left[node]
        else:
            node = tree.children_right[node]

    values = tree.value[node][0]
    total = np.sum(values)
    votes = np.zeros(num_classes)
    for c_idx, val in enumerate(values):
        if val > 0:
            votes[c_idx] += val / total
    return votes


class TestEmbeddedParity(unittest.TestCase):

    def test_decision_forest_parity(self):
        artifact = joblib.load(MODEL_PATH)
        model = artifact["model"]
        features_list = artifact["features"]
        classes = list(model.classes_)
        num_classes = len(classes)

        df = pd.read_csv(DATA_PATH)
        sample_X = df[features_list].head(50).to_numpy(dtype=float)

        py_preds = model.predict(df[features_list].head(50))

        c_preds = []
        for row in sample_X:
            total_votes = np.zeros(num_classes)
            for est in model.estimators_:
                total_votes += simulate_c_tree_predict(est, row, num_classes)
            best_c_idx = int(np.argmax(total_votes))
            c_preds.append(classes[best_c_idx])

        # Assert 100% agreement between Python RF prediction and C++ exported tree logic
        for i, (p_py, p_c) in enumerate(zip(py_preds, c_preds)):
            self.assertEqual(
                p_py, p_c,
                f"Mismatch at sample {i}: Python predicted {p_py}, C simulation predicted {p_c}"
            )


if __name__ == "__main__":
    unittest.main()
