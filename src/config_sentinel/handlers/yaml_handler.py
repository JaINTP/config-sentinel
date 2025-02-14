"""
YAML configuration file handler.

This module provides functionality for loading and saving configuration data in YAML format.
It implements the ConfigHandler interface to provide consistent configuration handling.
"""

# Standard library imports
from typing import Any, Dict
from pathlib import Path

# Third-party imports
import yaml

# Local imports
from config_sentinel.handlers.config_handler import ConfigHandler


class YAMLHandler(ConfigHandler):
    """
    Handler for YAML configuration files.

    This class implements the ConfigHandler interface for working with YAML format
    configuration files. It provides methods to load and save configuration data
    while handling common YAML-related errors.
    """

    def __init__(self, file_path: Path):
        """
        Initialize YAML handler.
        
        Args:
            file_path: Path to the YAML configuration file
        """
        self.file_path = file_path

    def load(self) -> Dict:
        """
        Load and parse the YAML configuration file.

        Returns:
            Dict: The configuration data loaded from the YAML file.

        Raises:
            ValueError: If the YAML file contains invalid syntax.
        """
        try:
            with open(self.file_path, "r") as f:
                content = f.read()
                # Explicitly check if content is non-empty but not valid YAML
                try:
                    data = yaml.safe_load(content)
                    if data is None and content.strip():  # Non-empty but invalid
                        raise ValueError("Failed to parse configuration: Invalid YAML content.")
                    return data or {}
                except yaml.YAMLError as e:
                    raise ValueError(f"Failed to parse configuration: {e}")
        except FileNotFoundError:
            return {}

    def save(self, data: Dict) -> None:
        """
        Save configuration data to a YAML file, overwriting any existing content.

        Args:
            data (Dict): The configuration data to save.

        Raises:
            OSError: If there is an error writing to the file.
            yaml.YAMLError: If the data cannot be serialized to YAML.
        """
        # Save the configuration, overwriting any existing content
        with open(self.file_path, "w") as f:
            yaml.safe_dump(data, f)