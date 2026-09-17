"""Main entry point script for real-time live Kendo analysis.

Architecture Pipeline:
  Camera Input (60 FPS)
    -> Pose & Shinai Extraction (MediaPipe/YOLO)
      -> State & Motion Lifecycle Tracker (FSM)
        ├─ Phase 1: Pre-Attack Kamae (Spine straight, stance width, arm angles)
        ├─ Phase 2: Motion Execution (Spine stability, head level, Ki-Ken-Tai-Ichi)
        └─ Phase 3: Post-Attack Zanshin (Recovery, Kensen on target, readiness)
    -> Integrated Score & Continuous Feedback
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path if executed directly
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from open_kendo.utils.config import ConfigLoader
from open_kendo.utils.logger import setup_logger


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for live runner."""
    parser = argparse.ArgumentParser(
        description="Open-Kendo: Real-time Kendo Technique Analysis (3-Phase Lifecycle)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/default.yaml",
        help="Path to configuration YAML file.",
    )
    parser.add_argument(
        "--weights",
        type=str,
        default="configs/weights.yaml",
        help="Path to scoring weights YAML file.",
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="Override camera index or input video file.",
    )
    return parser.parse_args()


def main() -> None:
    """Main execution loop template.

    Raises:
        NotImplementedError: Template shell awaiting implementation.
    """
    args = parse_args()
    logger = setup_logger("open_kendo.live")
    logger.info("Initializing Open-Kendo Live Analysis System (3-Phase Lifecycle)...")

    config = ConfigLoader.load_yaml(args.config)
    weights = ConfigLoader.load_yaml(args.weights)
    logger.info(f"Loaded configuration: {args.config} and weights: {args.weights}")

    # Pipeline template blueprint:
    # 1. VideoReader(source, target_fps=60)
    # 2. BasePoseEstimator (MediaPipePoseEstimator / YOLOPoseEstimator)
    # 3. ShinaiTracker()
    # 4. StateLifecycleTracker(config["lifecycle"])
    # 5. Phase Evaluators:
    #    - KamaeEvaluator(config["evaluation"]["kamae"])
    #    - KiKenTaiIchiEvaluator(config["evaluation"]["motion_execution"])
    #    - ZanshinEvaluator(config["evaluation"]["zanshin"])
    #    - KendoScorer(weights)
    # 6. FeedbackDashboard & VisualOverlayDrawer

    raise NotImplementedError(
        "Open-Kendo 3-Phase Lifecycle live pipeline loop is a template shell. "
        "Implement video processing loop in scripts/run_live.py."
    )


if __name__ == "__main__":
    main()
