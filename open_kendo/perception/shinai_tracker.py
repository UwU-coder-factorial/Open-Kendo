"""Shinai (bamboo sword) tracking module."""

from typing import Any, Dict, Optional
import numpy as np

from open_kendo.perception.base import (
    BaseObjectTracker,
    Point2D,
    PoseResult,
    TrackedObject,
)


class ShinaiTracker(BaseObjectTracker):
    """Tracks the Shinai blade, Kensen (tip), and Tsuka (hilt/grip).

    Supports multiple tracking modalities: color-geometry segmentation,
    optical flow tracking, or custom object detection.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize Shinai tracker with algorithm configuration.

        Args:
            config: Configuration containing tracking method, HSV ranges,
                    history buffer length, etc.
        """
        super().__init__(config=config)
        self.method: str = self.config.get("method", "color_geometry")
        self.track_history_length: int = self.config.get("track_history_length", 30)
        self._history: list[Point2D] = []

    def track(
        self,
        image: np.ndarray,
        pose_context: Optional[PoseResult] = None,
        timestamp_ms: float = 0.0,
    ) -> TrackedObject:
        """Track the Shinai tip, base, and blade line.

        Args:
            image: Current video frame (BGR format).
            pose_context: Pose keypoints (wrists/hands) used to anchor sword base.
            timestamp_ms: Monotonic timestamp in milliseconds.

        Returns:
            TrackedObject: Detected Shinai tip, base coordinates, and confidence.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("ShinaiTracker.track is not implemented.")

    def calculate_blade_vector(self, shinai: TrackedObject) -> Optional[np.ndarray]:
        """Compute the directional 2D/3D vector along the Shinai centerline.

        Args:
            shinai: Tracked Shinai object with detected tip and base.

        Returns:
            np.ndarray: Unit vector representing sword direction.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("ShinaiTracker.calculate_blade_vector is not implemented.")

    def reset(self) -> None:
        """Clear internal tracking history buffer.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("ShinaiTracker.reset is not implemented.")
