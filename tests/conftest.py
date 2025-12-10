"""
Pytest configuration and shared fixtures.

This module contains pytest configuration and fixtures that are used
across multiple test files.
"""

import pytest
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_env_vars(monkeypatch):
    """
    Fixture to set up mock environment variables for testing.

    Sets all required environment variables to test values to ensure
    tests don't rely on actual .env file configuration.
    """
    # First, set the environment variables
    env_vars = {
        # Flask configuration
        "FLASK_PORT": "5001",
        "FLASK_DEBUG": "False",
        "FLASK_HOST": "0.0.0.0",
        "POLL_INTERVAL": "2",
        "ENV": "test",
        # Tuya configuration
        "TUYA_ACCESS_ID": "test_access_id",
        "TUYA_ACCESS_SECRET": "test_access_secret",
        "TUYA_ENDPOINT": "https://openapi.tuyaus.com",
        "DEVICE_ID": "test_device_id",
        "TUYA_PULSAR_ENDPOINT": "wss://test.pulsar.com",
        # WhatsApp configuration
        "WA_API_URL": "https://api.whatsapp.test/send",
        "WA_API_USER": "test_user",
        "WA_API_PASSWORD": "test_password",
        "WA_GROUP_ID": "test_group_id",
        "WA_MESSAGE_DOOR_OPENED": "DOOR OPENED - Server room accessed",
        "WA_MESSAGE_DOOR_CLOSED": "DOOR CLOSED - Server room secured",
        "WA_MESSAGE_SENSOR_INITIALIZED": "SENSOR IS WORKING - Monitoring started",
        "WA_IS_FORWARDED": "false",
        "WA_DURATION": "0",
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    # Force reload of config module to pick up the new env vars
    # This is necessary because Config.py calls load_dotenv() at import time
    if "config.Config" in sys.modules:
        import importlib
        import config.Config

        importlib.reload(config.Config)

    # Also reload any modules that import from config to ensure they get the updated values
    modules_to_reload = ["services.tuya_service", "services.whatsapp_service", "main"]
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            import importlib

            module = sys.modules[module_name]
            importlib.reload(module)

    return env_vars


@pytest.fixture
def mock_tuya_api():
    """
    Fixture to create a mock TuyaOpenAPI instance.

    Returns a mock object that simulates TuyaOpenAPI behavior.
    """
    from unittest.mock import Mock

    mock = Mock()
    mock.access_id = "test_access_id"
    mock.access_secret = "test_access_secret"
    mock.endpoint = "https://openapi.tuyaus.com"
    mock.is_connect.return_value = True
    mock.connect.return_value = None

    return mock


@pytest.fixture
def sample_device_status():
    """
    Fixture providing sample device status response.

    Returns a typical successful response from Tuya API for device status.
    """
    return {
        "success": True,
        "result": [
            {"code": "doorcontact_state", "value": False},
            {"code": "battery_percentage", "value": 85},
        ],
        "msg": "success",
        "code": 200,
    }


@pytest.fixture
def sample_error_response():
    """
    Fixture providing sample error response.

    Returns a typical error response from Tuya API.
    """
    return {"success": False, "result": None, "msg": "Device not found", "code": 404}


@pytest.fixture
def flask_test_client():
    """
    Fixture providing a Flask test client.

    Creates a Flask application instance with test configuration
    and returns a test client for making requests.
    """
    from main import create_app

    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client
