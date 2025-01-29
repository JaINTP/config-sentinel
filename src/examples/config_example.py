"""Example module demonstrating configuration management with config_sentinel.

This module shows how to use the config_sentinel library to manage application configuration
using different file formats (JSON, TOML, YAML). It demonstrates:
- Defining configuration models with dataclasses
- Loading and saving configuration
- Accessing and modifying configuration values
- Working with different configuration file handlers
"""

# Standard library imports
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Type

# Third-party imports
from config_sentinel import Sentinel
from config_sentinel.handlers import (
    JSONHandler,
    TOMLHandler, 
    YAMLHandler
)


@dataclass
class UserConfig:
    """User configuration model.
    
    Attributes:
        username (Optional[str]): The username for authentication
        password (Optional[str]): The password for authentication
    """
    username: Optional[str] = 'Username'
    password: Optional[str] = 'Password'


@dataclass
class AppConfig:
    """Application configuration model.
    
    Attributes:
        app_name (str): The name of the application
        version (str): The version string
        debug (bool): Debug mode flag
        user (UserConfig): Nested user configuration
    """
    app_name: str = "MyApp"
    version: str = "1.0.0"
    debug: bool = False
    user: UserConfig = field(default_factory=UserConfig)


def handle_config(config_path: Path, handler_class: Type) -> None:
    """Handle configuration operations for a given file path and handler.
    
    Creates a configuration handler and sentinel, saves default config,
    and demonstrates getting/setting configuration values.
    
    Args:
        config_path: Path to the configuration file
        handler_class: The configuration handler class to use
        
    Returns:
        None
    """
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
    handlers = {
        "config.json": JSONHandler,
        "config.toml": TOMLHandler,
        "config.yaml": YAMLHandler
    }
    for path, handler_class in handlers.items():
        handle_config(Path(path), handler_class)
