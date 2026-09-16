"""Base classes and data models for perception modules."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import numpy as np


@dataclass
class Point2D:
    """2D Point coordinate normalized or in pixel space."""
    x: float
    y: float


@dataclass
class Point3D:
    """3D Point coordinate normalized or in metric/camera space."""
    x: float
    y: float
    z: float


@dataclass
class Keypoint:
    """Represents a detected anatomical landmark or keypoint."""
    name: str
    point_2d: Point2D
    point_3d: Optional[Point3D] = None
    confidence: float = 0.0
    visibility: float = 0.0


@dataclass
class PoseResult:
    """Encapsulates the complete human pose detected in a single frame."""
    keypoints: Dict[str, Keypoint] = field(default_factory=dict)
    bbox: Optional[List[float]] = None  # [xmin, ymin, xmax, ymax]
    timestamp_ms: float = 0.0
    is_detected: bool = False

    def get_keypoint(self, name: str) -> Optional[Keypoint]:
        """Retrieve keypoint by standard anatomical identifier."""
        return self.keypoints.get(name, None)


@dataclass
class TrackedObject:
    """Represents a tracked non-human object (e.g., Shinai tip, Tsuka)."""
    label: str
    center: Point2D
    bbox: Optional[List[float]] = None
    tip: Optional[Point2D] = None
    base: Optional[Point2D] = None
    confidence: float = 0.0
    trajectory: List[Point2D] = field(default_factory=list)


@dataclass
class FramePerceptionResult:
    """Combined perception output for one processed video frame."""
    frame_index: int
    timestamp_ms: float
    pose: Optional[PoseResult] = None
    shinai: Optional[TrackedObject] = None
    raw_frame_shape: Optional[List[int]] = None


class BasePoseEstimator(ABC):
    """Abstract interface for 2D/3D human pose estimators."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the pose estimator with backend configuration.

        Args:
            config: Optional configuration dictionary.
        """
        self.config = config or {}

    @abstractmethod
    def initialize(self) -> None:
        """Load models and allocate device resources.

        Raises:
            NotImplementedError: Must be implemented by concrete classes.
        """
        raise NotImplementedError("Subclasses must implement initialize()")

    @abstractmethod
    def estimate(self, image: np.ndarray, timestamp_ms: float = 0.0) -> PoseResult:
        """Perform pose estimation on a single RGB/BGR image frame.

        Args:
            image: Input image as a NumPy array (H, W, C).
            timestamp_ms: Monotonic timestamp of the frame in milliseconds.

        Returns:
            PoseResult: Structured anatomical keypoints and detection metadata.

        Raises:
            NotImplementedError: Must be implemented by concrete classes.
        """
        raise NotImplementedError("Subclasses must implement estimate()")

    @abstractmethod
    def release(self) -> None:
        """Release allocated inference resources and memory."""
        raise NotImplementedError("Subclasses must implement release()")


class BaseObjectTracker(ABC):
    """Abstract interface for object tracking (Shinai, Kensen, etc.)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize tracker with configuration.

        Args:
            config: Optional configuration dictionary.
        """
        self.config = config or {}

    @abstractmethod
    def track(
        self,
        image: np.ndarray,
        pose_context: Optional[PoseResult] = None,
        timestamp_ms: float = 0.0,
    ) -> TrackedObject:
        """Track target object leveraging optional human pose context.

        Args:
            image: Input image frame as NumPy array (H, W, C).
            pose_context: Optional pose detection for hand/wrist guidance.
            timestamp_ms: Monotonic timestamp in milliseconds.

        Returns:
            TrackedObject: Tracking result including tip, base, and confidence.

        Raises:
            NotImplementedError: Must be implemented by concrete classes.
        """
        raise NotImplementedError("Subclasses must implement track()")

    @abstractmethod
    def reset(self) -> None:
        """Reset internal tracking state and trajectory buffer."""
        raise NotImplementedError("Subclasses must implement reset()")
