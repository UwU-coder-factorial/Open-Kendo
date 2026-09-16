"""Ki-Ken-Tai-Ichi (Spirit, Sword, Body as One) synchronization evaluator."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from open_kendo.features.footwork import FootworkEvent
from open_kendo.features.kinematics import KinematicSnapshot
from open_kendo.features.trajectories import TrajectoryPoint


class SyncQuality(str, Enum):
    """Grading categories for Ki-Ken-Tai synchronization."""
    PERFECT = "perfect"          # Delta <= strict threshold (e.g., 40ms)
    GOOD = "good"                # Delta <= good threshold (e.g., 80ms)
    ACCEPTABLE = "acceptable"    # Delta <= acceptable window (e.g., 130ms)
    DESYNC = "desync"            # Out of sync (> 200ms)


@dataclass
class KiKenTaiIchiResult:
    """Quantitative measurement of Ki-Ken-Tai-Ichi synchronization."""
    ken_timestamp_ms: float          # Time of Shinai target impact peak
    tai_timestamp_ms: float          # Time of Fumikomi foot landing impact
    ki_posture_score: float          # Forward commitment & spine uprightness score
    delta_ms: float                  # Absolute time difference |t_ken - t_tai|
    sync_quality: SyncQuality
    lead_entity: str                 # "ken_early", "tai_early", or "simultaneous"
    score: float                     # Score normalized [0.0, 100.0]


class KiKenTaiIchiEvaluator:
    """Evaluates the time synchronization between sword strike, foot stomp, and spirit."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize evaluator with timing tolerance thresholds.

        Args:
            config: Optional configuration dictionary.
        """
        self.config = config or {}
        self.tolerance_ms: float = self.config.get("tolerance_ms", 120.0)
        self.strict_window_ms: float = self.config.get("strict_window_ms", 60.0)

    def evaluate_synchronization(
        self,
        ken_event: TrajectoryPoint,
        tai_event: FootworkEvent,
        posture_snapshot: KinematicSnapshot,
    ) -> KiKenTaiIchiResult:
        """Compute the synchronization delta between sword impact and foot stomp.

        Args:
            ken_event: Trajectory point representing the apex/impact of the Shinai cut.
            tai_event: Footwork event representing the Fumikomi landing impact.
            posture_snapshot: Kinematic snapshot of body posture at impact instant.

        Returns:
            KiKenTaiIchiResult: Evaluated delta, quality classification, and score.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("KiKenTaiIchiEvaluator.evaluate_synchronization is not implemented.")

    def compute_sync_score(self, delta_ms: float) -> float:
        """Map time delta (in milliseconds) to a non-linear score between 0 and 100.

        Args:
            delta_ms: Absolute difference in milliseconds between events.

        Returns:
            float: Score in range [0.0, 100.0].

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("KiKenTaiIchiEvaluator.compute_sync_score is not implemented.")
