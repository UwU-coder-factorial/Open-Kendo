"""Real-time Heads-Up Display (HUD) dashboard for Kendo practitioner feedback."""

from typing import Any, Dict, Optional
import numpy as np

from open_kendo.evaluation.kikentaichi import KiKenTaiIchiResult
from open_kendo.evaluation.models import StrikeEvaluationResult


class FeedbackDashboard:
    """Renders real-time HUD metrics, sync gauges, score cards, and FPS counter."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize HUD dashboard with layout coordinates and dimensions.

        Args:
            config: Configuration dictionary with UI display parameters.
        """
        self.config = config or {}
        self.hud_bg_color = tuple(self.config.get("colors", {}).get("hud_bg", [25, 25, 25]))

    def render_hud(
        self,
        frame: np.ndarray,
        fps: float,
        last_strike: Optional[StrikeEvaluationResult] = None,
        last_sync: Optional[KiKenTaiIchiResult] = None,
    ) -> np.ndarray:
        """Draw complete HUD elements on the upper and lower margins of frame.

        Args:
            frame: Target BGR image frame.
            fps: Current measured processing frame rate.
            last_strike: Most recent completed strike evaluation result.
            last_sync: Real-time sync measurement for current motion phase.

        Returns:
            np.ndarray: Modified frame with complete dashboard HUD.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("FeedbackDashboard.render_hud is not implemented.")

    def render_sync_gauge(
        self,
        frame: np.ndarray,
        sync_result: KiKenTaiIchiResult,
        position: tuple[int, int],
    ) -> np.ndarray:
        """Draw a visual gauge indicating Ken vs Tai timing offset.

        Green center indicates synchronized strike ('Ichi'); left/right drift indicates
        early sword or early foot.

        Args:
            frame: Target BGR image frame.
            sync_result: Synchronization measurement.
            position: Top-left coordinate (x, y) for gauge component.

        Returns:
            np.ndarray: Frame with sync gauge rendered.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("FeedbackDashboard.render_sync_gauge is not implemented.")
