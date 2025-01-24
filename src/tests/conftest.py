# tests/conftest.py
# Custom pytest configuration file.

import os

def pytest_sessionfinish(session, exitstatus):
    """
    Hook to execute a command after the pytest session finishes.
    
    :param session: The pytest session object.
    :param exitstatus: The exit status of the pytest session.
    """
    os.system("uv run coverage-badge -f -o assets/coverage.svg")
