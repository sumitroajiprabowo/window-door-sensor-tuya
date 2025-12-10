"""
Tuya Service - Tuya Cloud API Integration

This module provides a service layer for interacting with the Tuya Cloud API.
It handles authentication, connection management, and device operations such as
querying status and sending commands to IoT devices.
"""

from tuya_connector import TuyaOpenAPI
from config.Config import TuyaConfig
import logging


class TuyaService:
    """
    Service class for Tuya Cloud API operations.

    Manages connection to Tuya Cloud and provides methods to interact
    with IoT devices through the Tuya OpenAPI.
    """

    def __init__(self):
        """
        Initialize Tuya service with API credentials.

        Creates a TuyaOpenAPI instance and establishes initial connection
        using credentials from configuration.
        """
        self.openapi = TuyaOpenAPI(
            TuyaConfig.API_ENDPOINT,
            TuyaConfig.ACCESS_ID,
            TuyaConfig.ACCESS_SECRET,
        )
        self.connect()

    def connect(self):
        """
        Establish or verify connection to Tuya Cloud.

        Attempts to connect to Tuya Cloud if not already connected.
        Logs connection status and any errors encountered.
        """
        try:
            if not self.openapi.is_connect():
                self.openapi.connect()
                logging.info("Connected to Tuya Cloud")
        except Exception as e:
            logging.error(f"Failed to connect to Tuya Cloud: {e}")

    def is_authenticated(self):
        """
        Verify if the current credentials are valid.

        Checks if valid API credentials are configured and if the
        connection to Tuya Cloud is active.

        Returns:
            bool: True if authenticated and connected, False otherwise
        """
        # Check if credentials are set and not placeholder values
        if not self.openapi.access_id or self.openapi.access_id == "your_access_id":
            return False

        # Verify active connection with valid token
        return self.openapi.is_connect()

    def get_device_status(self, device_id):
        """
        Retrieve current status of a Tuya device.

        Queries the Tuya Cloud API for the current state of all device
        properties including sensor readings and battery level.

        Args:
            device_id (str): The unique identifier of the device

        Returns:
            dict: API response containing device status data
        """
        self.connect()
        response = self.openapi.get(f"/v1.0/devices/{device_id}/status")
        return response

    def send_command(self, device_id, commands):
        """
        Send control commands to a Tuya device.

        Sends one or more commands to control device behavior through
        the Tuya Cloud API.

        Args:
            device_id (str): The unique identifier of the device
            commands (list): List of command dictionaries to execute

        Returns:
            dict: API response indicating command execution status
        """
        self.connect()
        response = self.openapi.post(
            f"/v1.0/devices/{device_id}/commands", {"commands": commands}
        )
        return response


# Global singleton instance for application-wide use
tuya_service = TuyaService()
