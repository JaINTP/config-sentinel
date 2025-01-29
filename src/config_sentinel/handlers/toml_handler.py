"""
TOML configuration file handler.

This module provides functionality for loading and saving configuration data in TOML format.
It implements the ConfigHandler interface to provide consistent configuration handling.
"""

# Standard library imports
from typing import Any, Dict, List, Union

# Third-party imports
from tomli import TOMLDecodeError, load as toml_load
from tomli_w import dump as toml_dump

# Local imports
from config_sentinel.handlers.config_handler import ConfigHandler


class TOMLHandler(ConfigHandler):
    """
    Handler for TOML configuration files.

    This class implements the ConfigHandler interface for working with TOML format
    configuration files. It provides methods to load and save configuration data
    while handling common TOML-related errors.
    """

    def load(self) -> Dict:
        """
        Load and parse the TOML configuration file.

        Returns:
            Dict: The configuration data loaded from the TOML file.

        Raises:
            ValueError: If the TOML file contains invalid syntax.
        """
        def restore_none(data: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
            """
            Recursively restore empty strings to None values in the data structure.

            Args:
                data: The data structure to process.

            Returns:
                The processed data structure with empty strings converted to None.
            """
            if isinstance(data, dict):
                return {k: restore_none(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [restore_none(v) for v in data]
            return None if data == "" else data

        try:
            with open(self.file_path, "rb") as f:
                data = toml_load(f)
                return restore_none(data)
        except FileNotFoundError:
            return {}
        except TOMLDecodeError as e:
            raise ValueError(f"Failed to parse configuration: {e}")

    def save(self, data: Dict) -> None:
        """
        Save configuration data to a TOML file.

        Args:
            data: The configuration data to save.

        Raises:
            OSError: If there is an error writing to the file.
            TypeError: If the data contains objects that cannot be serialized to TOML.
        """
        def replace_none(data: Union[Dict, List, Any]) -> Union[Dict, List, Any]:
            """
            Recursively replace None values with empty strings in the data structure.

            Args:
                data: The data structure to process.

            Returns:
                The processed data structure with None values converted to empty strings.
            """
            if isinstance(data, dict):
                return {k: replace_none(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [replace_none(v) for v in data]
            return "" if data is None else data

        serialized_data = replace_none(data)
        with open(self.file_path, "wb") as f:
            toml_dump(serialized_data, f)
