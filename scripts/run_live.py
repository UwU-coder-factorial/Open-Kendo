"""Main entry point script for real-time live Kendo analysis.

Connects Camera -> Perception -> Feature Extraction -> Ki-Ken-Tai-Ichi Evaluation -> UI Overlay.
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
        description="Open-Kendo: Real-time Kendo Technique Analysis"
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
    """Main execution loop (skeleton).

    Raises:
        NotImplementedError: Template shell awaiting implementation.
    """
    args = parse_args()
    logger = setup_logger("open_kendo.live")
    logger.info("Initializing Open-Kendo Live Analysis System...")

    config = ConfigLoader.load_yaml(args.config)
    logger.info(f"Loaded configuration from: {args.config}")

    # Pipeline initialization placeholder:
    # 1. Initialize VideoReader(source)
    # 2. Initialize PoseEstimator (MediaPipe / YOLO)
    # 3. Initialize ShinaiTracker
    # 4. Initialize Feature Calculators (Kinematics, Trajectory, Footwork)
    # 5. Initialize Evaluators (KiKenTaiIchi, DTW, Scorer)
    # 6. Initialize UI Overlay & HUD

    raise NotImplementedError(
        "Open-Kendo live pipeline main loop is a template shell. "
        "Implement video processing loop in scripts/run_live.py."
    )


if __name__ == "__main__":
    main()
