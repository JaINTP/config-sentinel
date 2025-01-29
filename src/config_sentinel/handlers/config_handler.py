"""
Configuration handler interface for different file formats.

This module provides an abstract base class that defines the interface for configuration
handlers. Each handler implementation must provide methods for loading and saving
configuration data in their specific format.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union


class ConfigHandler(ABC):
    """
    Abstract base class defining the interface for configuration handlers.

    This class provides the base interface that all configuration handlers must implement.
    It defines methods for loading and saving configuration data, while leaving the
    specific implementation details to the concrete handler classes.

    Attributes:
        file_path (Path): The path to the configuration file.
    """

    def __init__(self, file_path: Union[str, Path]):
        """
        Initialize the configuration handler.

        Args:
            file_path (Union[str, Path]): Path to the configuration file. Can be provided
                as either a string or Path object.
        """
        self.file_path = Path(file_path)  # Ensure file_path is a Path object

    @abstractmethod
    def load(self):
        """
        Load and parse the configuration from the file.

        Returns:
            dict: The configuration data loaded from the file.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
            ValueError: If the file contains invalid configuration data.
        """
        pass

    @abstractmethod
    def save(self, data: dict):
        """
        Save the configuration data to the file.

        Args:
            data (dict): The configuration data to save.

        Raises:
            OSError: If there is an error writing to the file.
            ValueError: If the data cannot be serialized to the file format.
        """
        pass
