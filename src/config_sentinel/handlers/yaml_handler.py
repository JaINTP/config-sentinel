# handlers/yaml_handler.py
from pathlib import Path

import yaml

from .config_handler import ConfigHandler

class YAMLHandler(ConfigHandler):
    """
    YAML file handler implementation of ConfigHandler.
    """

    def load(self) -> dict:
        if not self.file_path.exists():
            return {}
        with self.file_path.open('r') as f:
            return yaml.safe_load(f)

    def save(self, data: dict):
        with open(self.file_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)