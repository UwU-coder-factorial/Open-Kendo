"""Tests for utility modules."""

from pathlib import Path
import pytest

from open_kendo.utils.config import ConfigLoader
from open_kendo.utils.logger import setup_logger
from open_kendo.utils.video_io import VideoReader, VideoWriter


def test_config_loader_reads_default_yaml():
    """Verify default.yaml can be parsed into dictionary."""
    config_path = Path("configs/default.yaml")
    if config_path.exists():
        cfg = ConfigLoader.load_yaml(config_path)
        assert isinstance(cfg, dict)
        assert "perception" in cfg
        assert "evaluation" in cfg


def test_config_loader_missing_file():
    """Verify loading non-existent config raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        ConfigLoader.load_yaml("configs/non_existent_config.yaml")


def test_logger_setup():
    """Verify logger setup produces valid logger object."""
    logger = setup_logger("test_open_kendo")
    assert logger.name == "test_open_kendo"


def test_video_reader_writer_interfaces():
    """Verify VideoReader and VideoWriter raise NotImplementedError on abstract operations."""
    reader = VideoReader(source=0)
    with pytest.raises(NotImplementedError):
        reader.open()

    writer = VideoWriter(output_path="test.mp4")
    with pytest.raises(NotImplementedError):
        writer.open()
