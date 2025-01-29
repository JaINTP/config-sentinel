"""Test module for the Sentinel configuration management system.

This module contains comprehensive test cases for the Sentinel class, which provides configuration
management functionality with support for different file formats (JSON, TOML, YAML).

The test suite covers:
- Initialization and singleton pattern behavior
- File handling and persistence
- Configuration updates and validation
- Nested configuration access
- Error handling and edge cases
- File watching and monitoring
- Configuration merging and preservation
- Type validation and conversion

Each test case is designed to verify a specific aspect of the Sentinel's functionality
while maintaining isolation and independence from other tests.
"""

# Standard library imports
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Tuple

# Third-party imports
import pytest

# Local imports
from config_sentinel.handlers.json_handler import JSONHandler
from config_sentinel.handlers.toml_handler import TOMLHandler
from config_sentinel.handlers.yaml_handler import YAMLHandler
from config_sentinel.sentinel import Sentinel


@dataclass
class UserConfig:
    """
    Configuration model for user-related settings.
    
    Attributes:
        username (Optional[str]): The username for authentication, defaults to None
        password (Optional[str]): The password for authentication, defaults to None
    """
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class AppConfig:
    """
    Configuration model for application settings.
    
    Attributes:
        app_name (str): The name of the application, defaults to "MyApp"
        version (str): The version of the application, defaults to "1.0.0"
        debug (bool): Debug mode flag, defaults to False
        user (UserConfig): Nested user configuration, defaults to empty UserConfig
    """
    app_name: str = "MyApp"
    version: str = "1.0.0"
    debug: bool = False
    user: UserConfig = field(default_factory=UserConfig)


@pytest.fixture(autouse=True)
def reset_sentinel() -> None:
    """
    Reset the Sentinel singleton before each test.
    
    This fixture ensures each test starts with a clean Sentinel instance
    by clearing the singleton instance between tests.
    """
    Sentinel._instance = None


@pytest.fixture(params=["json", "toml", "yaml"])
def sentinel_and_handler(request, tmp_path) -> Tuple[Sentinel, object, Path]:
    """
    Provide a Sentinel instance and handler for different file formats.

    Creates a new Sentinel instance with appropriate handler for each supported
    file format, using a temporary directory for test files.

    Args:
        request: Pytest request object containing the file format parameter
        tmp_path: Temporary directory path for test files

    Returns:
        Tuple containing:
            - Sentinel instance configured for testing
            - Handler instance for file operations
            - Path to the temporary config file
    """
    file_extension = request.param
    file_path = tmp_path / f"config.{file_extension}"
    handler_class = {"json": JSONHandler, "toml": TOMLHandler, "yaml": YAMLHandler}[file_extension]
    handler = handler_class(file_path)
    sentinel = Sentinel(config_model=AppConfig, handler=handler)
    return sentinel, handler, file_path


def test_sentinel_initialization(sentinel_and_handler: Tuple[Sentinel, object, Path]) -> None:
    """
    Test proper initialization of Sentinel with default values.
    
    Verifies that:
    - Default configuration values are set correctly
    - Configuration file is created automatically
    - Singleton pattern is maintained
    
    Args:
        sentinel_and_handler: Fixture providing test components
    """
    sentinel, _, file_path = sentinel_and_handler

    # Verify default values on first run
    assert sentinel.get("app_name") == "MyApp"
    assert sentinel.get("user.username") is None

    # Verify file creation
    assert file_path.exists(), "Config file should be created with default values."


def test_sentinel_missing_config_file(sentinel_and_handler: Tuple[Sentinel, object, Path]) -> None:
    """
    Test Sentinel behavior when config file is missing.
    
    Verifies that:
    - Missing configuration file is handled gracefully
    - Default values are used when file is missing
    - New configuration file is created automatically
    
    Args:
        sentinel_and_handler: Fixture providing test components
    """
    sentinel, handler, file_path = sentinel_and_handler

    if file_path.exists():
        file_path.unlink()

    sentinel = Sentinel(config_model=AppConfig, handler=handler)

    # Force config save
    sentinel.save_config()

    # Verify defaults
    assert sentinel.get("app_name") == "MyApp"
    assert sentinel.get("user.username") is None

    # Verify file creation
    assert file_path.exists()


def test_sentinel_set_and_get(sentinel_and_handler: Tuple[Sentinel, object, Path]) -> None:
    """
    Test setting and getting configuration values.
    
    Verifies that:
    - Configuration values can be updated
    - Updated values can be retrieved correctly
    - Both simple and nested values work properly
    
    Args:
        sentinel_and_handler: Fixture providing test components
    """
    sentinel, _, _ = sentinel_and_handler

    # Update configuration
    sentinel.set("user.username", "admin_user")
    sentinel.set("debug", True)

    # Verify updates
    assert sentinel.get("user.username") == "admin_user"
    assert sentinel.get("debug") is True


def test_sentinel_to_dict(sentinel_and_handler: Tuple[Sentinel, object, Path]) -> None:
    """
    Test conversion of configuration to dictionary format.
    
    Verifies that:
    - Configuration can be converted to dictionary
    - Nested structures are preserved in conversion
    - All values are correctly represented
    
    Args:
        sentinel_and_handler: Fixture providing test components
    """
    sentinel, _, _ = sentinel_and_handler

    # Update configuration
    sentinel.set("user.password", "new_password")

    # Convert to dictionary
    config_dict = sentinel.to_dict()
    assert config_dict["user"]["password"] == "new_password"
    assert config_dict["app_name"] == "MyApp"


def test_sentinel_nested_update(sentinel_and_handler: Tuple[Sentinel, object, Path]) -> None:
    """
    Test updating nested configuration values.
    
    Verifies that:
    - Nested configuration values can be updated
    - Updates preserve the structure
    - Nested values can be retrieved correctly
    
    Args:
        sentinel_and_handler: Fixture providing test components
    """
    sentinel, _, _ = sentinel_and_handler

    # Update nested configuration
    sentinel.set("user.username", "nested_user")
    sentinel.set("user.password", "nested_pass")

    # Verify nested updates
    assert sentinel.get("user.username") == "nested_user"
    assert sentinel.get("user.password") == "nested_pass"


def test_sentinel_invalid_key(sentinel_and_handler: Tuple[Sentinel, object, Path]) -> None:
    """
    Test handling of invalid configuration keys.
    
    Verifies that:
    - Invalid keys raise appropriate exceptions
    - Nested key validation works correctly
    - None value handling is proper
    
    Args:
        sentinel_and_handler: Fixture providing test components
    """
    sentinel, _, _ = sentinel_and_handler

    # Test invalid nested key
    with pytest.raises(KeyError, match=r"Invalid configuration key: non"):
        sentinel.set("non.existent.key", "value")

    # Set an intermediate key to None
    sentinel.set("user", None)

    # Test behavior when accessing a nested key of a None field
    with pytest.raises(KeyError, match=r"Intermediate key 'user' is None in path: user.username"):
        sentinel.set("user.username", "value")

    # Test invalid field under a valid key
    with pytest.raises(KeyError, match=r"Intermediate key 'user' is None in path: user.invalid_field"):
        sentinel.set("user.invalid_field", "value")


def test_sentinel_inspect_caller(sentinel_and_handler: Tuple[Sentinel, object, Path], caplog) -> None:
    """
    Test caller inspection functionality.
    
    Verifies that:
    - Caller inspection logging works
    - Warning messages are properly formatted
    - Logging level is correct
    
    Args:
        sentinel_and_handler: Fixture providing test components
        caplog: Pytest fixture for capturing log output
    """
    sentinel, _, _ = sentinel_and_handler

    with caplog.at_level(logging.WARNING):
        sentinel.set("app_name", "CallerTestApp", inspect_caller=True)

    # Verify log output
    assert "Sentinel.set() called by" in caplog.text


def test_sentinel_merge_preserves_existing_values(sentinel_and_handler: Tuple[Sentinel, object, Path]) -> None:
    """
    Test that merging configurations preserves existing values.
    
    Verifies that:
    - Existing values are preserved during merges
    - New values are properly added
    - Updated values are correctly reflected
    
    Args:
        sentinel_and_handler: Fixture providing test components
    """
    sentinel, handler, file_path = sentinel_and_handler

    # Initial save with some values
    sentinel.set("app_name", "InitialApp")
    sentinel.set("user.username", "existing_user")
    sentinel.save_config()

    # Modify the config file directly to simulate external updates
    updated_config = {
        "app_name": "UpdatedApp",  # This should update
        "user": {
            "password": "new_password"  # This should add without overwriting username
        },
        "debug": True  # This should add
    }
    handler.save(updated_config)

    # Reload configuration
    sentinel._load_config()

    # Verify the merge behavior
    assert sentinel.get("app_name") == "UpdatedApp"  # Updated
    assert sentinel.get("user.username") == "existing_user"  # Preserved
    assert sentinel.get("user.password") == "new_password"  # Added
    assert sentinel.get("debug") is True  # Added


def test_from_dict_invalid_input(sentinel_and_handler: Tuple[Sentinel, object, Path]) -> None:
    """
    Test handling of invalid input in from_dict method.
    
    Verifies that:
    - Invalid input types are properly rejected
    - Appropriate exceptions are raised
    - Error messages are descriptive
    
    Args:
        sentinel_and_handler: Fixture providing test components
    """
    sentinel, _, _ = sentinel_and_handler

    # Invalid type (non-dict) passed to _from_dict
    with pytest.raises(TypeError, match="Expected a dictionary for dataclass"):
        sentinel._from_dict("invalid input")

    # Non-dataclass config model
    sentinel.config_model = str  # Assign a non-dataclass type
    with pytest.raises(ValueError, match="is not a valid dataclass"):
        sentinel._from_dict({})


def test_set_invalid_key_handling(sentinel_and_handler: Tuple[Sentinel, object, Path]) -> None:
    """
    Test handling of invalid keys in set method.
    
    Verifies that:
    - Invalid keys are properly detected
    - Appropriate exceptions are raised
    - None value handling is correct
    
    Args:
        sentinel_and_handler: Fixture providing test components
    """
    sentinel, _, _ = sentinel_and_handler

    # Test invalid key
    with pytest.raises(KeyError, match=r"Invalid configuration key: non"):
        sentinel.set("nonexistent.key", "value")

    # Test intermediate key being None
    sentinel.set("user", None)
    with pytest.raises(KeyError, match=r"Intermediate key 'user' is None in path: user.username"):
        sentinel.set("user.username", "value")


def test_stop_watching(sentinel_and_handler: Tuple[Sentinel, object, Path], caplog) -> None:
    """
    Test stopping the file watcher functionality.
    
    Verifies that:
    - File watching can be stopped safely
    - Proper logging occurs
    - No exceptions are raised
    
    Args:
        sentinel_and_handler: Fixture providing test components
        caplog: Pytest fixture for capturing log output
    """
    sentinel, _, _ = sentinel_and_handler

    with caplog.at_level(logging.INFO):
        # Ensure no exceptions are raised when stopping the observer
        sentinel.stop_watching()

    # Verify log output
    assert "Stopping file observer." in caplog.text
