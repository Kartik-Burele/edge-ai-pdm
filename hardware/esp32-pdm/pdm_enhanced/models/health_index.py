"""Health Index calculation module for predictive maintenance of DC motors.

Converts multi-class fault probabilities and anomaly scores into a standardized
0 - 100% Health Index, with clear operating states and severity alarms.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping
import numpy as np


@dataclass(frozen=True)
class HealthStatus:
    health_index: float           # 0.0 to 100.0%
    state: str                    # "NOMINAL", "WARNING", "CRITICAL"
    primary_condition: str        # e.g., "Healthy", "F2 - Step load increase"
    confidence_percent: float     # 0.0 to 100.0%
    is_anomaly: bool              # True if uncalibrated/novel behavior
    fault_probabilities: dict[str, float]  # Class probability distribution


FAULT_DISPLAY_NAMES = {
    "HEALTHY": "Healthy (Normal Operation)",
    "F1": "F1: Repeat Load Step",
    "F2": "F2: Step Load Increase",
    "F3": "F3: Current Spike",
    "F4": "F4: Undervoltage",
    "UNKNOWN_ANOMALY": "Unknown / Uncalibrated Anomaly",
}

NOMINAL_THRESHOLD = 80.0
WARNING_THRESHOLD = 50.0


def compute_health_index(
    class_probabilities: Mapping[str, float],
    is_anomaly: bool = False,
) -> HealthStatus:
    """Calculate the continuous health index and operating state from model probabilities.
    
    Health Index = 100 * P(HEALTHY), penalized if anomaly is flagged.
    """
    p_healthy = float(class_probabilities.get("HEALTHY", 0.0))
    p_faults = sum(
        p for k, p in class_probabilities.items() if k != "HEALTHY"
    )

    # Base Health Index (0 to 100%)
    health_idx = max(0.0, min(100.0, p_healthy * 100.0))
    if is_anomaly:
        health_idx = min(health_idx, 40.0)

    # Determine top predicted class and confidence
    best_class = max(class_probabilities, key=lambda k: class_probabilities[k])
    best_conf = float(class_probabilities[best_class]) * 100.0

    if is_anomaly and best_conf < 70.0:
        primary_condition = FAULT_DISPLAY_NAMES["UNKNOWN_ANOMALY"]
        state = "CRITICAL"
    elif health_idx >= NOMINAL_THRESHOLD:
        primary_condition = FAULT_DISPLAY_NAMES.get(best_class, best_class)
        state = "NOMINAL"
    elif health_idx >= WARNING_THRESHOLD:
        primary_condition = FAULT_DISPLAY_NAMES.get(best_class, best_class)
        state = "WARNING"
    else:
        primary_condition = FAULT_DISPLAY_NAMES.get(best_class, best_class)
        state = "CRITICAL"

    return HealthStatus(
        health_index=round(health_idx, 2),
        state=state,
        primary_condition=primary_condition,
        confidence_percent=round(best_conf, 2),
        is_anomaly=is_anomaly,
        fault_probabilities={k: round(float(v), 4) for k, v in class_probabilities.items()},
    )
