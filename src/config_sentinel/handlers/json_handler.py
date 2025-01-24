# handler/json_handler.py

import json

from .config_handler import ConfigHandler

class JSONHandler(ConfigHandler):

    def load(self) -> dict:
        if not self.file_path.exists():
            return {}
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def save(self, data: dict):
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)