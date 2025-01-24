# handlers/toml_handler.py

from tomli_w import dump as toml_dump
from tomli import load as toml_load, TOMLDecodeError

from .config_handler import ConfigHandler

class TOMLHandler(ConfigHandler):
    def load(self):
        def restore_none(data):
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

    def save(self, data: dict):
        def replace_none(data):
            if isinstance(data, dict):
                return {k: replace_none(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [replace_none(v) for v in data]
            return "" if data is None else data

        serialized_data = replace_none(data)
        with open(self.file_path, "wb") as f:
            toml_dump(serialized_data, f)
