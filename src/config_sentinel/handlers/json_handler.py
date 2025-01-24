# handler/json_handler.py

import json

from .config_handler import ConfigHandler

class JSONHandler(ConfigHandler):

    def load(self):
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse configuration: {e}")
        except FileNotFoundError:
            return {}


    def save(self, data: dict):
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)