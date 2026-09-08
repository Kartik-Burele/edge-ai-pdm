"""Out-of-Distribution (OOD) / Anomaly Detector for Predictive Maintenance.

Uses an Isolation Forest trained strictly on Healthy baseline feature distributions
to detect unexpected vibration, current, or RPM signatures before classification.
"""

from __future__ import annotations
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler


class MotorAnomalyDetector:
    """Outlier / Novelty detector fitted on healthy baseline data."""

    def __init__(self, contamination: float = 0.02, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.scaler = RobustScaler()
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1,
        )
        self.features: list[str] = []

    def fit(self, X_healthy: pd.DataFrame) -> MotorAnomalyDetector:
        """Fit scaler and Isolation Forest on healthy baseline features."""
        self.features = list(X_healthy.columns)
        X_scaled = self.scaler.fit_transform(X_healthy)
        self.model.fit(X_scaled)
        return self

    def predict_anomaly(self, X: pd.DataFrame) -> np.ndarray:
        """Return boolean array: True if anomalous / out-of-distribution, False otherwise."""
        X_sub = X[self.features]
        X_scaled = self.scaler.transform(X_sub)
        preds = self.model.predict(X_scaled)  # +1 for inlier, -1 for outlier
        return preds == -1

    def anomaly_score(self, X: pd.DataFrame) -> np.ndarray:
        """Return continuous anomaly score: lower values indicate higher abnormality."""
        X_sub = X[self.features]
        X_scaled = self.scaler.transform(X_sub)
        return self.model.decision_function(X_scaled)

    def save(self, filepath: str | Path) -> None:
        """Save fitted detector artifact."""
        joblib.dump(
            {
                "scaler": self.scaler,
                "model": self.model,
                "features": self.features,
                "contamination": self.contamination,
            },
            filepath,
        )

    @classmethod
    def load(cls, filepath: str | Path) -> MotorAnomalyDetector:
        """Load fitted detector from artifact."""
        data = joblib.load(filepath)
        obj = cls(contamination=data["contamination"])
        obj.scaler = data["scaler"]
        obj.model = data["model"]
        obj.features = data["features"]
        return obj
