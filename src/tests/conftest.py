"""
Custom pytest configuration module.

This module contains pytest hooks and configuration settings for test execution.
It handles tasks like generating coverage badges after test runs.
"""

# Standard library imports
import os


def pytest_sessionfinish(session, exitstatus):
    """
    Execute commands after the pytest session finishes.
    
    This hook runs after all tests complete to generate a coverage badge.
    
    Args:
        session: The pytest session object containing test execution info
        exitstatus (int): The exit status code from the test run
        
    Returns:
        None
    """
    os.system("uv run coverage-badge -f -o assets/coverage.svg")
