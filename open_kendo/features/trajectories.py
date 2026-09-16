"""Trajectory tracking and temporal smoothing for Kendo motion paths."""

from collections import deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List, Optional
import numpy as np

from open_kendo.perception.base import Point2D


@dataclass
class TrajectoryPoint:
    """A spatial point sampled at a specific timestamp."""
    point: Point2D
    timestamp_ms: float
    velocity: float = 0.0
    acceleration: float = 0.0


class TrajectoryBuffer:
    """Maintains a rolling temporal buffer of 2D coordinates with smoothing."""

    def __init__(
        self,
        buffer_size: int = 60,
        smoothing_method: str = "moving_average",
        smoothing_window: int = 5,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize trajectory buffer with smoothing configurations.

        Args:
            buffer_size: Maximum number of points to retain in rolling buffer.
            smoothing_method: Filtering method ("moving_average", "savitzky_golay", "kalman").
            smoothing_window: Window size for smoothing filters.
            config: Optional configuration dictionary.
        """
        self.buffer_size = buffer_size
        self.smoothing_method = smoothing_method
        self.smoothing_window = smoothing_window
        self.config = config or {}
        self._buffer: Deque[TrajectoryPoint] = deque(maxlen=buffer_size)

    def append(self, point: Point2D, timestamp_ms: float) -> None:
        """Add new point to buffer and compute velocity relative to previous point.

        Args:
            point: 2D position in frame.
            timestamp_ms: Monotonic timestamp in milliseconds.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("TrajectoryBuffer.append is not implemented.")

    def get_smoothed_points(self) -> List[Point2D]:
        """Apply configured smoothing filter over the buffered points.

        Returns:
            List[Point2D]: Filtered sequence of coordinates.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("TrajectoryBuffer.get_smoothed_points is not implemented.")

    def get_peak_velocity(self) -> Optional[TrajectoryPoint]:
        """Find the point in the buffer where velocity reached its maximum peak.

        Crucial for pinpointing the exact frame of Shinai strike impact apex.

        Returns:
            Optional[TrajectoryPoint]: The trajectory point corresponding to peak velocity.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("TrajectoryBuffer.get_peak_velocity is not implemented.")

    def clear(self) -> None:
        """Clear all buffered trajectory points."""
        self._buffer.clear()
