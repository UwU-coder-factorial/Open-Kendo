"""Utility script to record Sensei/Master gold-standard strikes for DTW reference."""

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
    """Parse command line arguments for master recorder."""
    parser = argparse.ArgumentParser(
        description="Open-Kendo: Record Gold-Standard Master Reference Strikes"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/gold_standards/men_sensei.npz",
        help="Destination path for saving gold-standard kinematic time series.",
    )
    parser.add_argument(
        "--technique",
        type=str,
        default="men",
        choices=["men", "kote", "do", "tsuki", "suburi"],
        help="Target strike technique to label.",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="0",
        help="Camera index or path to high-speed recording video file.",
    )
    return parser.parse_args()


def main() -> None:
    """Master strike extraction workflow (skeleton).

    Raises:
        NotImplementedError: Template shell awaiting implementation.
    """
    args = parse_args()
    logger = setup_logger("open_kendo.recorder")
    logger.info(f"Preparing to record Gold-Standard: '{args.technique.upper()}' to {args.output}")

    # Master recording placeholder:
    # 1. Capture clean strike sequence
    # 2. Extract normalized pose keypoints and Shinai tip trajectory
    # 3. Save multi-dimensional time series array using np.savez_compressed

    raise NotImplementedError(
        "Open-Kendo master strike recording workflow is a template shell. "
        "Implement recording pipeline in scripts/record_master.py."
    )


if __name__ == "__main__":
    main()
