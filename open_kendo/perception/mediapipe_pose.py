"""MediaPipe implementation wrapper for human pose estimation."""

from typing import Any, Dict, Optional
import numpy as np

from open_kendo.perception.base import BasePoseEstimator, PoseResult


class MediaPipePoseEstimator(BasePoseEstimator):
    """Pose estimator utilizing Google MediaPipe Pose Landmarker solutions."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize MediaPipe pose estimator with parameters.

        Args:
            config: Configuration dictionary containing model_complexity,
                    min_detection_confidence, min_tracking_confidence, etc.
        """
        super().__init__(config=config)
        self.model_complexity: int = self.config.get("model_complexity", 2)
        self.min_detection_confidence: float = self.config.get("min_detection_confidence", 0.7)
        self.min_tracking_confidence: float = self.config.get("min_tracking_confidence", 0.7)
        self._detector: Any = None

    def initialize(self) -> None:
        """Instantiate MediaPipe Pose pipeline.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("MediaPipePoseEstimator.initialize is not implemented.")

    def estimate(self, image: np.ndarray, timestamp_ms: float = 0.0) -> PoseResult:
        """Run MediaPipe pose inference on input frame.

        Args:
            image: Image in BGR or RGB format.
            timestamp_ms: Frame timestamp in milliseconds.

        Returns:
            PoseResult: Standardized Kendo body keypoints.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("MediaPipePoseEstimator.estimate is not implemented.")

    def release(self) -> None:
        """Close MediaPipe detector instance and free resources.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("MediaPipePoseEstimator.release is not implemented.")
