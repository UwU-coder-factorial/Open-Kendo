"""Ultralytics YOLO Pose wrapper for real-time human pose estimation."""

from typing import Any, Dict, Optional
import numpy as np

from open_kendo.perception.base import BasePoseEstimator, PoseResult


class YOLOPoseEstimator(BasePoseEstimator):
    """Pose estimator utilizing Ultralytics YOLOv8/v11 Pose neural networks."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize YOLO pose estimator.

        Args:
            config: Configuration dictionary containing model_path,
                    confidence_threshold, device, etc.
        """
        super().__init__(config=config)
        self.model_path: str = self.config.get("model_path", "models/yolov8n-pose.pt")
        self.confidence_threshold: float = self.config.get("confidence_threshold", 0.6)
        self.device: str = self.config.get("device", "cuda")
        self._model: Any = None

    def initialize(self) -> None:
        """Load YOLO model checkpoint onto the designated compute device.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("YOLOPoseEstimator.initialize is not implemented.")

    def estimate(self, image: np.ndarray, timestamp_ms: float = 0.0) -> PoseResult:
        """Run YOLO pose inference on a single image.

        Args:
            image: Image in BGR or RGB format.
            timestamp_ms: Monotonic timestamp in milliseconds.

        Returns:
            PoseResult: Keypoints translated to Kendo anatomical joints.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("YOLOPoseEstimator.estimate is not implemented.")

    def release(self) -> None:
        """Clear model from memory and GPU VRAM.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("YOLOPoseEstimator.release is not implemented.")
