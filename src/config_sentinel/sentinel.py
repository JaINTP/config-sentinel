# sentinel.py

import inspect
import logging
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Type, Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .handlers import ConfigHandler


class Sentinel(FileSystemEventHandler):
    _instance = None
    configuration: Optional[Any] = None  # Holds the user-defined config object

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Sentinel, cls).__new__(cls)
        return cls._instance

    def __init__(self, config_model: Type[Any], handler: ConfigHandler):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self.logger.propagate = True

        self.config_model = config_model
        self.handler = handler
        self.file_path = handler.file_path
        self._observer = Observer()

        self._load_config()

        self._observer.schedule(self, path=self.file_path.parent, recursive=False)
        self._observer.start()
        self._initialized = True

    def _load_config(self):
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
        Preserves existing values and fills missing fields with defaults.
        """
        def merge_instance(cls, values, instance=None):
            if not is_dataclass(cls):
                self.logger.debug(f"Non-dataclass type encountered: {cls}. Returning value as-is.")
                return values

            if not isinstance(values, dict):
                raise TypeError(f"Expected a dictionary for dataclass {cls}, got {type(values).__name__}")

            if not hasattr(cls, "__dataclass_fields__"):
                raise ValueError(f"{cls} is not a valid dataclass.")

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

        try:
            self.logger.debug(f"Deserializing with config_model: {self.config_model} and data: {data}")
            instance = merge_instance(self.config_model, data, self.configuration)
            self.logger.debug(f"Merged configuration: {instance}")
            return instance
        except Exception as e:
            self.logger.error(f"Failed to merge configuration: {e}")
            raise

    def _save_default_config(self):
        """
        Save the default configuration to the file.
        """
        self.save_config()

    def save_config(self):
        """
        Save the current configuration object to the file.
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
        """
        return self._to_dict(self.configuration)

    def _to_dict(self, obj: Any) -> dict:
        """
        Convert a user-defined configuration object into a dictionary.
        Handles nested dataclasses and lists.
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
        Automatically initializes intermediate `None` keys as needed.
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
                    # Dynamically initialize nested dataclass
                    field_type = type(config).__dataclass_fields__[k].type
                    sub_config = field_type()
                    setattr(config, k, sub_config)
                config = sub_config
            else:
                raise KeyError(f"Invalid configuration key: {'.'.join(keys[:keys.index(k) + 1])}")

        last_key = keys[-1]
        if hasattr(config, last_key):
            setattr(config, last_key, value)
        else:
            raise KeyError(f"Invalid configuration key: {key}")

        self.save_config()
        self.logger.info(f"Updated configuration key '{key}' to '{value}'.")


    def stop_watching(self):
        """
        Stop the file observer.
        """
        self.logger.info("Stopping file observer.")
        self._observer.stop()
        self._observer.join()
