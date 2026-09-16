"""OpenCV-based visual overlay rendering for skeleton, sword, and annotations."""

from typing import Any, Dict, List, Optional
import numpy as np

from open_kendo.perception.base import Point2D, PoseResult, TrackedObject


class VisualOverlayDrawer:
    """Renders kinematic overlays, skeleton connections, and trajectory ribbons onto OpenCV frames."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize drawer with color theme and line styles.

        Args:
            config: Configuration defining colors, line thickness, font scale.
        """
        self.config = config or {}
        self.skeleton_color = tuple(self.config.get("colors", {}).get("skeleton", [0, 255, 128]))
        self.shinai_color = tuple(self.config.get("colors", {}).get("shinai", [0, 200, 255]))

    def draw_skeleton(
        self,
        frame: np.ndarray,
        pose: PoseResult,
        highlight_faults: bool = True,
    ) -> np.ndarray:
        """Render anatomical joint lines with color-coded posture feedback.

        Args:
            frame: BGR image frame (H, W, 3).
            pose: Detected pose keypoints.
            highlight_faults: Highlight misaligned joints (e.g., bent back) in red.

        Returns:
            np.ndarray: Modified frame with skeleton overlay.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("VisualOverlayDrawer.draw_skeleton is not implemented.")

    def draw_shinai_trajectory(
        self,
        frame: np.ndarray,
        trajectory: List[Point2D],
        fade_effect: bool = True,
    ) -> np.ndarray:
        """Draw motion trail ribbon tracing the Shinai tip (Kensen).

        Args:
            frame: Target BGR image frame.
            trajectory: Sequence of recent Shinai tip coordinates.
            fade_effect: Whether older trail segments fade into transparency.

        Returns:
            np.ndarray: Frame with trajectory ribbon overlay.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("VisualOverlayDrawer.draw_shinai_trajectory is not implemented.")

    def draw_impact_indicator(
        self,
        frame: np.ndarray,
        impact_point: Point2D,
        target_name: str,
        is_ippon: bool,
    ) -> np.ndarray:
        """Draw visual flash / target ring at the point of impact.

        Args:
            frame: Target BGR image frame.
            impact_point: Coordinate where strike landed.
            target_name: Target label ("MEN", "KOTE", "DO", "TSUKI").
            is_ippon: Whether the strike satisfied Ippon criteria.

        Returns:
            np.ndarray: Frame with impact marker.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("VisualOverlayDrawer.draw_impact_indicator is not implemented.")
