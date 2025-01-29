"""
A module for managing configuration files with automatic reloading capabilities.

This module provides a singleton class that handles configuration file management,
including loading, saving, and watching for changes. It supports nested dataclasses
and provides dot notation access to configuration values.
"""

# Standard imports
import inspect
import logging
from dataclasses import asdict, is_dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Optional, Type

# Third-party imports
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Local imports
from config_sentinel.handlers import ConfigHandler


class Sentinel(FileSystemEventHandler):
    """
    A singleton class that manages configuration files with automatic reloading.

    This class implements the FileSystemEventHandler to watch for file changes and
    provides methods to load, save, and access configuration values. It supports
    nested dataclasses and provides dot notation access to configuration values.

    Attributes:
        _instance: The singleton instance of the class.
        configuration: The user-defined configuration object.
        config_model: The dataclass type used for the configuration.
        handler: The ConfigHandler instance used for file operations.
        file_path: The path to the configuration file.
        _observer: The file system observer for watching config changes.
        logger: The logger instance for this class.
        _lock: A lock for thread-safe operations.
    """

    _instance = None
    configuration: Optional[Any] = None  # Holds the user-defined config object

    def __new__(cls, *args, **kwargs):
        """Create or return the singleton instance of the class."""
        if not cls._instance:
            cls._instance = super(Sentinel, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_model: Type[Any], handler: ConfigHandler):
        """
        Initialize the Sentinel instance.

        Args:
            config_model: The dataclass type used for the configuration.
            handler: The ConfigHandler instance used for file operations.
        """
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self.logger.propagate = True

        self.config_model = config_model
        self.handler = handler
        self.file_path = handler.file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._observer = Observer()
        self._lock = Lock()
        self._load_config()
        self._observer.schedule(self, path=self.file_path.parent, recursive=False)
        self._observer.start()
        self._initialized = True

    def _load_config(self):
        """
        Load the configuration from file or create default if file is empty/invalid.
        """
        with self._lock:
            try:
                data = self.handler.load()
                if not data:
                    self.logger.warning(f"Configuration file {self.file_path} is empty. Using defaults.")
                    self.configuration = self.config_model()
                    self.save_config()  # Ensure file creation
                else:
                    self.configuration = self._from_dict(data)
                self.logger.info("Configuration loaded successfully.")
            except Exception as e:
                self.logger.error(f"Failed to load configuration: {e}")
                self.configuration = self.config_model()
                self.save_config()

    def _from_dict(self, data: dict) -> Any:
        """
        Merge a dictionary into a user-defined configuration object.

        Args:
            data: The dictionary containing configuration values.

        Returns:
            The merged configuration object.

        Raises:
            ValueError: If the config_model is not a valid dataclass.
            TypeError: If the input data is not a dictionary.
        """
        def merge_instance(cls, values, instance=None):
            if not is_dataclass(cls):
                raise ValueError(f"{cls} is not a valid dataclass.")

            if not isinstance(values, dict):
                raise TypeError(f"Expected a dictionary for dataclass {cls}, got {type(values).__name__}")

            field_types = {f.name: f.type for f in cls.__dataclass_fields__.values()}
            if instance is None:
                instance = cls()

            self.logger.debug(f"Merging into {cls.__name__} with instance: {instance} and values: {values}")

            for key, field_type in field_types.items():
                try:
                    if key in values:
                        value = values[key]
                        if is_dataclass(field_type) and isinstance(value, dict):
                            nested_instance = getattr(instance, key, None)
                            setattr(instance, key, merge_instance(field_type, value, nested_instance))
                        else:
                            setattr(instance, key, value)
                    elif not hasattr(instance, key) or getattr(instance, key) is None:
                        default_value = getattr(cls(), key)
                        setattr(instance, key, default_value)
                except Exception as e:
                    self.logger.error(f"Error merging key '{key}' in {cls.__name__}: {e}")
                    raise

            return instance

        if not is_dataclass(self.config_model):
            raise ValueError(f"{self.config_model} is not a valid dataclass.")

        try:
            self.logger.debug(f"Deserializing with config_model: {self.config_model} and data: {data}")
            instance = merge_instance(self.config_model, data, self.configuration)
            self.logger.debug(f"Merged configuration: {instance}")
            return instance
        except Exception as e:
            self.logger.error(f"Failed to merge configuration: {e}")
            raise

    def _save_default_config(self):
        """Save the default configuration to the file."""
        self.save_config()

    def save_config(self):
        """
        Save the current configuration object to the file.

        Raises:
            Exception: If saving the configuration fails.
        """
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            data = self._to_dict(self.configuration)
            self.logger.debug(f"Serialized configuration: {data}")  # Debug output
            self.handler.save(data)
            self.logger.info("Configuration saved successfully.")
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {e}")

    def to_dict(self) -> dict:
        """
        Convert the configuration object into a dictionary.

        Returns:
            A dictionary representation of the configuration.
        """
        return self._to_dict(self.configuration)

    def _to_dict(self, obj: Any) -> dict:
        """
        Convert a user-defined configuration object into a dictionary.

        Args:
            obj: The configuration object to convert.

        Returns:
            A dictionary representation of the object.

        Raises:
            TypeError: If the object type is not supported.
        """
        def recursive_asdict(o):
            if is_dataclass(o):
                return {k: recursive_asdict(v) for k, v in asdict(o).items()}
            elif isinstance(o, list):
                return [recursive_asdict(i) for i in o]
            elif isinstance(o, dict):
                return {k: recursive_asdict(v) for k, v in o.items()}
            return '' if o is None else o

        if is_dataclass(obj):
            return recursive_asdict(obj)
        raise TypeError(f"Unsupported configuration object type: {type(obj)}")

    def get(self, key: str, default=None) -> Any:
        """
        Retrieve a configuration value using dot notation.

        Args:
            key: The configuration key in dot notation.
            default: The default value to return if key doesn't exist.

        Returns:
            The configuration value or the default value.
        """
        keys = key.split(".")
        value = self.configuration
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        return value

    def set(self, key: str, value: Any, inspect_caller=False):
        """
        Update a configuration value using dot notation and save the configuration.

        Args:
            key: The configuration key in dot notation.
            value: The value to set.
            inspect_caller: Whether to log the caller information.

        Raises:
            KeyError: If the key path is invalid or an intermediate key is None.
        """
        if inspect_caller:
            stack = inspect.stack()
            caller_frame = stack[1]
            caller_module = inspect.getmodule(caller_frame[0])
            caller_name = caller_frame.function
            module_name = caller_module.__name__ if caller_module else "UnknownModule"

            self.logger.warning(
                f"Sentinel.set() called by {module_name}.{caller_name} "
                f"trying to set {key} to {value}"
            )

        keys = key.split(".")
        config = self.configuration

        for k in keys[:-1]:
            if hasattr(config, k):
                sub_config = getattr(config, k)
                if sub_config is None:
                    raise KeyError(f"Intermediate key '{k}' is None in path: {key}")
                config = sub_config
            else:
                full_key = ".".join(keys[:keys.index(k) + 1])
                raise KeyError(f"Invalid configuration key: {full_key}")

        last_key = keys[-1]
        if hasattr(config, last_key):
            setattr(config, last_key, value)
        else:
            raise KeyError(f"Invalid configuration key: {key}")

        self.save_config()
        self.logger.info(f"Updated configuration key '{key}' to '{value}'.")

    def stop_watching(self):
        """Stop the file observer and join its thread."""
        self.logger.info("Stopping file observer.")
        self._observer.stop()
        self._observer.join()

    def on_modified(self, event):
        """
        Handle file modification events.
        
        Args:
            event: The file system event that triggered this handler.
        """
        if event.src_path == str(self.file_path):
            self.logger.debug("Configuration file change detected, attempting reload...")
            try:
                self._load_config()
                self.logger.info("Configuration successfully reloaded")
            except Exception as e:
                self.logger.error(f"Failed to reload configuration: {e}")
