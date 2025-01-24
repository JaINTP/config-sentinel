import os
import pytest
from pathlib import Path

from config_sentinel.handlers import JSONHandler, TOMLHandler, YAMLHandler


@pytest.fixture(params=["json", "toml", "yaml"])
def handler_and_file(request, tmp_path) -> tuple:
    """
    Provide handler class and temporary file path for different formats.
    """
    file_extension = request.param
    file_path = tmp_path / f"config.{file_extension}"
    handler_class = {"json": JSONHandler, "toml": TOMLHandler, "yaml": YAMLHandler}[file_extension]
    return handler_class(file_path), file_path


def test_handler_load_save_with_edge_cases(handler_and_file):
    handler, file_path = handler_and_file

    # Data with edge cases
    edge_case_data = {
        "app_name": "EdgeCaseApp",
        "numbers": [1, 2, 3],
        "nested": {"key": None, "list": []},
        "empty": {},
        "boolean": True
    }

    # Save and reload data
    handler.save(edge_case_data)
    loaded_data = handler.load()

    # Verify that all values, including None, are preserved
    assert loaded_data == edge_case_data, "Loaded data should match saved data, including None values."


def test_handler_empty_load(handler_and_file):
    handler, file_path = handler_and_file

    # Ensure file is empty
    if file_path.exists():
        file_path.unlink()

    # Load data from an empty file
    data = handler.load()
    assert data == {}, "Loading from a non-existent file should return an empty dictionary."


def test_handler_invalid_file_content(handler_and_file):
    handler, file_path = handler_and_file

    # Write unambiguous invalid YAML content
    with open(file_path, "w") as f:
        f.write(": this is clearly invalid yaml")

    # Expect an exception when loading invalid content
    with pytest.raises(ValueError, match="Failed to parse configuration"):
        handler.load()


def test_handler_overwrite_data(handler_and_file):
    handler, file_path = handler_and_file

    # Save initial data
    initial_data = {"app_name": "OldApp", "version": "1.0.0"}
    handler.save(initial_data)

    # Save new data
    new_data = {"app_name": "NewApp", "debug": True}
    handler.save(new_data)

    # Verify file content is replaced
    loaded_data = handler.load()
    assert loaded_data == new_data, "File content should be replaced with new data."

def test_handler_nested_data_structure(handler_and_file):
    handler, file_path = handler_and_file

    # Nested data structure
    nested_data = {
        "app_name": "NestedApp",
        "settings": {
            "theme": "dark",
            "features": {"logging": True, "notifications": False}
        }
    }

    # Save and reload data
    handler.save(nested_data)
    loaded_data = handler.load()
    assert loaded_data == nested_data, "Loaded nested data should match saved nested data."


def test_handler_read_only_file(handler_and_file):
    handler, file_path = handler_and_file

    # Save valid data
    data = {"key": "value"}
    handler.save(data)

    # Make the file read-only
    os.chmod(file_path, 0o444)

    # Attempt to save and expect a failure
    with pytest.raises(PermissionError, match="Permission denied"):
        handler.save({"new_key": "new_value"})

    # Revert permissions to avoid test issues
    os.chmod(file_path, 0o666)
