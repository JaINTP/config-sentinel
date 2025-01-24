from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Type

from config_sentinel import Sentinel
from config_sentinel.handlers import JSONHandler, TOMLHandler, YAMLHandler


@dataclass
class UserConfig:
    username: Optional[str] = 'Username'
    password: Optional[str] = 'Password'


@dataclass
class AppConfig:
    app_name: str = "MyApp"
    version: str = "1.0.0"
    debug: bool = False
    user: UserConfig = field(default_factory=UserConfig)


def handle_config(config_path: Path, handler_class: Type):
    handler = handler_class(config_path)
    sentinel = Sentinel(config_model=AppConfig, handler=handler)
    sentinel.save_config()

    print(f"Configuration: {config_path}")
    print(f"App Name: {sentinel.get('app_name')}")
    print(f"Username: {sentinel.get('user.username')}")

    sentinel.set("user.username", "admin")
    print(f"Updated Username: {sentinel.get('user.username')}")

    print(f"Configuration: {sentinel.to_dict()}")
    print()


if __name__ == "__main__":
    handlers = {"config.json": JSONHandler, "config.toml": TOMLHandler, "config.yaml": YAMLHandler}
    for path, handler_class in handlers.items():
        handle_config(Path(path), handler_class)
