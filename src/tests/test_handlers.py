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


def test_handler_load_save(handler_and_file):
    handler, file_path = handler_and_file

    # Initial data to save
    initial_data = {
        "app_name": "TestApp",
        "version": "2.0.0",
        "debug": True,
        "user": {"username": "test_user", "password": "secure_pass"}
    }

    # Save data
    handler.save(initial_data)
    assert file_path.exists(), "Config file should be created."

    # Load data
    loaded_data = handler.load()
    assert loaded_data == initial_data, "Loaded data should match saved data."


def test_handler_empty_load(handler_and_file):
    handler, file_path = handler_and_file

    # Ensure file is empty
    if file_path.exists():
        file_path.unlink()

    # Load data from an empty file
    data = handler.load()
    assert data == {}, "Loading from a non-existent file should return an empty dictionary."
