# handlers/yaml_handler.py

import yaml
from yaml.parser import ParserError
from yaml.scanner import ScannerError

from .config_handler import ConfigHandler


class YAMLHandler(ConfigHandler):
    def load(self):
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

    def save(self, data: dict):
        with open(self.file_path, "w") as f:
            yaml.safe_dump(data, f)
