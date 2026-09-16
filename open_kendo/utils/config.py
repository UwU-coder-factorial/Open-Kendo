"""Configuration loader and schema management."""

from pathlib import Path
from typing import Any, Dict, Optional, Union
import yaml


class ConfigLoader:
    """Loads and validates YAML configuration files."""

    @staticmethod
    def load_yaml(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Load and parse a YAML file safely.

        Args:
            file_path: Path to the YAML file.

        Returns:
            Dict[str, Any]: Parsed configuration dictionary.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            yaml.YAMLError: If parsing encounters invalid YAML syntax.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path.resolve()}")

        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config or {}

    @classmethod
    def merge_configs(cls, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge override dictionary into base configuration.

        Args:
            base: Base configuration dictionary.
            override: Override dictionary with updated values.

        Returns:
            Dict[str, Any]: Merged configuration dictionary.

        Raises:
            NotImplementedError: Template shell awaiting implementation.
        """
        raise NotImplementedError("ConfigLoader.merge_configs is not implemented.")
