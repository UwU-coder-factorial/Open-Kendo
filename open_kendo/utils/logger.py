"""Structured logging utility for Open-Kendo."""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "open_kendo",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Configure and return a structured logger instance.

    Args:
        name: Name of the logger hierarchy.
        level: Logging level (e.g. logging.DEBUG, logging.INFO).
        log_file: Optional path to write log records to disk.

    Returns:
        logging.Logger: Configured logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if log_file:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "open_kendo") -> logging.Logger:
    """Retrieve an existing logger or create one with default settings."""
    return logging.getLogger(name)
