"""
Configuration Module - Application Settings

This module loads and manages all application configuration from environment
variables. It provides three configuration classes: Flask app settings,
Tuya IoT Platform credentials, and WhatsApp API credentials.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Flask application configuration.

    Provides settings for the Flask web server including host, port,
    debug mode, and polling intervals for device monitoring.
    """

    # Flask web server settings
    PORT = int(os.getenv("FLASK_PORT", 5001))
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"  # Production mode by default
    HOST = os.getenv("FLASK_HOST", "0.0.0.0")

    # Device polling configuration
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 2))  # Seconds between status checks

    # Application environment (production or development)
    ENV = os.getenv("ENV", "production")


class TuyaConfig:
    """
    Tuya IoT Platform configuration.

    Contains authentication credentials and endpoints for accessing the
    Tuya Cloud API and connecting to IoT devices.
    """

    # Tuya Cloud API credentials
    ACCESS_ID = os.getenv("TUYA_ACCESS_ID")
    ACCESS_SECRET = os.getenv("TUYA_ACCESS_SECRET")
    API_ENDPOINT = os.getenv("TUYA_ENDPOINT")

    # Target device identifier
    DEVICE_ID = os.getenv("DEVICE_ID")

    # Pulsar WebSocket endpoint (optional - currently using HTTP polling)
    TUYA_PULSAR_ENDPOINT = os.getenv("TUYA_PULSAR_ENDPOINT")

    @classmethod
    def validate(cls):
        """
        Validate that all required Tuya configuration is present.

        Raises:
            ValueError: If any required configuration value is missing
        """
        required = ["ACCESS_ID", "ACCESS_SECRET", "API_ENDPOINT", "DEVICE_ID"]
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(
                f"Missing required Tuya configuration: {', '.join(missing)}"
            )


class WhatsAppConfig:
    """
    WhatsApp API configuration.

    Contains credentials and endpoints for sending WhatsApp messages
    via the WhatsApp Business API when door events are detected.
    """

    # WhatsApp API connection settings
    API_URL = os.getenv("WA_API_URL")
    API_USER = os.getenv("WA_API_USER")
    API_PASSWORD = os.getenv("WA_API_PASSWORD")

    # Target WhatsApp group for notifications
    GROUP_ID = os.getenv("WA_GROUP_ID")

    # Customizable alert messages
    MESSAGE_DOOR_OPENED = os.getenv(
        "WA_MESSAGE_DOOR_OPENED", "DOOR OPENED - Server room accessed"
    )
    MESSAGE_DOOR_CLOSED = os.getenv(
        "WA_MESSAGE_DOOR_CLOSED", "DOOR CLOSED - Server room secured"
    )
    MESSAGE_SENSOR_INITIALIZED = os.getenv(
        "WA_MESSAGE_SENSOR_INITIALIZED", "SENSOR IS WORKING - Monitoring started"
    )

    # Optional message parameters
    IS_FORWARDED = os.getenv("WA_IS_FORWARDED", "false").lower() == "true"
    DURATION = int(os.getenv("WA_DURATION", "0"))  # 0 means don't include in payload

    @classmethod
    def validate(cls):
        """
        Validate that all required WhatsApp configuration is present.

        Raises:
            ValueError: If any required configuration value is missing
        """
        required = ["API_URL", "API_USER", "API_PASSWORD", "GROUP_ID"]
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(
                f"Missing required WhatsApp configuration: {', '.join(missing)}"
            )
