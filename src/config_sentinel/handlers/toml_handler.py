# handlers/toml_handler.py

import tomli
import tomli_w

from .config_handler import ConfigHandler

class TOMLHandler(ConfigHandler):
    def load(self) -> dict:
        if not self.file_path.exists():
            return {}
        with open(self.file_path, 'rb') as f:
            return tomli.load(f)

    def save(self, data: dict):
        with open(self.file_path, 'wb') as f:
            tomli_w.dump(data, f)