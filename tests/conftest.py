"""
Pytest configuration and shared fixtures.

This module provides common test fixtures and configuration for the entire test suite.
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path
from typing import Generator, Dict, Any
from unittest.mock import patch

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create an instance of the default event loop for the test session.
    This ensures async tests work properly.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_env_vars() -> Dict[str, str]:
    """
    Provide test environment variables.
    Returns a dictionary of environment variables for testing.
    """
    return {
        "MONGODB_URL": "mongodb://localhost:27017",
        "MONGODB_DATABASE": "blog_reviewer_test",
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "DEBUG",
        "TESTING": "true"
    }


@pytest.fixture(scope="function")
def mock_env_vars(test_env_vars: Dict[str, str]) -> Generator[None, None, None]:
    """
    Mock environment variables for individual tests.
    This fixture patches os.environ for the duration of a test.
    """
    with patch.dict(os.environ, test_env_vars, clear=False):
        yield


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment() -> Generator[None, None, None]:
    """
    Set up test environment automatically for all tests.
    This fixture runs before any tests and cleans up after.
    """
    # Setup
    original_env = os.environ.copy()
    
    # Set test-specific environment variables
    os.environ["TESTING"] = "true"
    os.environ["ENVIRONMENT"] = "test"
    
    yield
    
    # Cleanup
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture(scope="function")
def temp_config_file(tmp_path: Path) -> Path:
    """
    Create a temporary configuration file for testing.
    Returns the path to the temporary config file.
    """
    config_file = tmp_path / "test_config.env"
    config_content = """
# Test configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=blog_reviewer_test
ENVIRONMENT=test
LOG_LEVEL=DEBUG
"""
    config_file.write_text(config_content.strip())
    return config_file


# Pytest marks for different test categories
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.docker = pytest.mark.docker
pytest.mark.mongodb = pytest.mark.mongodb
pytest.mark.slow = pytest.mark.slow


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Register custom markers
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (require services)"
    )
    config.addinivalue_line(
        "markers", "e2e: End-to-end tests (full system)"
    )
    config.addinivalue_line(
        "markers", "docker: Tests requiring Docker services"
    )
    config.addinivalue_line(
        "markers", "mongodb: Tests requiring MongoDB"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        
        # Add docker marker for integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.docker)
            
        # Add mongodb marker for database tests
        if "mongodb" in item.name.lower() or "mongo" in str(item.fspath).lower():
            item.add_marker(pytest.mark.mongodb)


@pytest.fixture(scope="function")
def mock_mongodb_client():
    """
    Mock MongoDB client for unit tests.
    This prevents unit tests from requiring actual MongoDB connection.
    """
    from unittest.mock import MagicMock
    
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()
    
    mock_client.return_value = mock_client
    mock_client.__getitem__ = lambda self, name: mock_db
    mock_db.__getitem__ = lambda self, name: mock_collection
    
    with patch("pymongo.MongoClient", return_value=mock_client):
        yield mock_client