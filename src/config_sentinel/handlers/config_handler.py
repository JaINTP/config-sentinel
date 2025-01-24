from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union
from pydantic import BaseModel


class ConfigHandler(ABC):
    """
    Abstract base class for configuration handlers.
    """

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)  # Ensure file_path is a Path object

    @abstractmethod
    def load(self):
        """
        Load the configuration from the file.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def save(self, data: dict):
        """
        Save the configuration to the file.
        Must be implemented by subclasses.
        """
        pass
