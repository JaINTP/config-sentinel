"""
JSON configuration file handler.

This module provides functionality for loading and saving configuration data in JSON format.
It implements the ConfigHandler interface to provide consistent configuration handling.
"""

# Standard library imports
import json
from typing import Dict

# Local imports
from config_sentinel.handlers.config_handler import ConfigHandler


class JSONHandler(ConfigHandler):
    """
    Handler for JSON configuration files.

    This class implements the ConfigHandler interface for working with JSON format
    configuration files. It provides methods to load and save configuration data
    while handling common JSON-related errors.
    """

    def load(self) -> Dict:
        """
        Load and parse the JSON configuration file.

        Returns:
            Dict: The configuration data loaded from the JSON file.

        Raises:
            ValueError: If the JSON file contains invalid syntax.
        """
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse configuration: {e}")
        except FileNotFoundError:
            return {}

    def save(self, data: Dict) -> None:
        """
        Save configuration data to a JSON file.

        Args:
            data (Dict): The configuration data to save.

        Raises:
            OSError: If there is an error writing to the file.
            TypeError: If the data contains objects that cannot be serialized to JSON.
        """
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)