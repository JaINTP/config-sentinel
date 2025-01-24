# Config Sentinel
[![GitHub - Jai Brown](https://img.shields.io/badge/GitHub-jaintp-181717.svg?style=flat&logo=github)](https://github.com/jaintp)
![Coverage](assets/coverage.svg)

---

**Config Sentinel** is a robust and feature-rich Python library for seamless configuration management. It supports JSON, YAML, and TOML formats and simplifies dynamic configuration handling with real-time file watching, intuitive dot-notation access, and Pydantic-powered schema validation. Whether you're building simple scripts or complex applications, Config Sentinel provides the tools to keep your configurations dynamic and maintainable.

---

## Features

- **Multiple Formats**: Manage configurations in JSON, YAML, or TOML formats effortlessly.
- **Real-Time Watching**: Automatically reload configurations upon file changes.
- **Dot-Notation Access**: Easily access and update nested configuration values using dot-notation.
- **Validation**: Ensure configurations meet your schema requirements with Pydantic validation.
- **Developer-Friendly**: Plug-and-play with minimal setup and comprehensive examples.

## TODO List

- [ ] Add callback support for configuration file modifications.
- [ ] Add event integration for enhanced file modification handling.

## Installation

To install Config Sentinel, clone the repository and use the `uv` tool:

```bash
# Clone the repository
git clone https://github.com/jaintp/config-sentinel.git

# Navigate to the project directory
cd config-sentinel

# Install the project
uv install
```

## Usage

Here is a basic example of using Config Sentinel to manage configurations:

```python
from dataclasses import dataclass, field
from pathlib import Path
from config_sentinel import Sentinel
from config_sentinel.handlers import YAMLHandler

# Define a configuration schema
@dataclass
class AppConfig:
    app_name: str = "MyApp"
    version: str = "1.0.0"
    debug: bool = False
    user: dict = field(default_factory=lambda: {"username": None, "password": None})

# Initialize Sentinel
config_path = Path("config.yaml")
handler = YAMLHandler(config_path)
sentinel = Sentinel(config_model=AppConfig, handler=handler)

# Access configuration values
print(sentinel.get("app_name"))

# Update configuration values
sentinel.set("user.username", "admin")
sentinel.save_config()
```

## Running Tests

To ensure everything works as expected, run the tests with pytest:

```bash
pytest
```

For coverage:

```bash
pytest --cov=config_sentinel --cov-report=term-missing
```

## Project Structure

```
config-sentinel/
├── src/
│   ├── config_sentinel/
│   │   ├── __init__.py
│   │   ├── sentinel.py
│   │   ├── handlers/
│   │       ├── __init__.py
│   │       ├── json_handler.py
│   │       ├── yaml_handler.py
│   │       ├── toml_handler.py
├── tests/
│   ├── test_handlers.py
│   ├── test_sentinel.py
├── examples/
│   ├── config_example.py
├── pyproject.toml
├── README.md
```

## Development

To contribute:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature description"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Create a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Author

Developed by Jai Brown (JaINTP) (<jaintp.dev@gmail.com>)