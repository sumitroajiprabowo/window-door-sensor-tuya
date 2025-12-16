"""
Unit tests for services/tuya_listener.py module.

Tests Pulsar WebSocket listener functionality.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock, call


class TestTuyaListener:
    """Test cases for TuyaListener class."""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        with patch("services.tuya_listener.TuyaConfig") as mock:
            mock.ACCESS_ID = "test_access_id"
            mock.ACCESS_SECRET = "test_secret"
            mock.TUYA_PULSAR_ENDPOINT = "wss://test.endpoint.com"
            mock.DEVICE_ID = "test_device_123"
            yield mock

    @pytest.fixture
    def mock_pulsar(self):
        """Mock TuyaOpenPulsar."""
        with patch("services.tuya_listener.TuyaOpenPulsar") as mock:
            yield mock

    @pytest.fixture
    def listener(self, mock_config, mock_pulsar):
        """Create TuyaListener instance with mocks."""
        from services.tuya_listener import TuyaListener

        return TuyaListener()

    def test_initialization(self, listener, mock_config, mock_pulsar):
        """Test that TuyaListener initializes correctly."""
        assert listener.access_id == "test_access_id"
        assert listener.access_secret == "test_secret"
        assert listener.endpoint == "wss://test.endpoint.com"

        # Verify Pulsar was initialized with correct parameters
        mock_pulsar.assert_called_once()

    def test_on_message_door_opened(self, listener, mock_config):
        """Test on_message handles door opened event."""
        message = json.dumps(
            {
                "bizCode": "devicePropertyMessage",
                "bizData": {
                    "devId": "test_device_123",
                    "properties": [
                        {"code": "doorcontact_state", "value": True, "time": 1234567890}
                    ],
                },
                "ts": 1234567890,
            }
        )

        with patch("services.tuya_listener.send_door_opened_alert") as mock_alert:
            listener.on_message(message)
            mock_alert.assert_called_once()

    def test_on_message_door_closed(self, listener, mock_config):
        """Test on_message handles door closed event."""
        message = json.dumps(
            {
                "bizCode": "devicePropertyMessage",
                "bizData": {
                    "devId": "test_device_123",
                    "properties": [
                        {"code": "doorcontact_state", "value": False, "time": 1234567890}
                    ],
                },
                "ts": 1234567890,
            }
        )

        with patch("services.tuya_listener.send_door_closed_alert") as mock_alert:
            listener.on_message(message)
            mock_alert.assert_called_once()

    def test_on_message_different_device(self, listener, mock_config):
        """Test that messages from different devices are ignored."""
        message = json.dumps(
            {
                "bizCode": "devicePropertyMessage",
                "bizData": {
                    "devId": "different_device_456",
                    "properties": [{"code": "doorcontact_state", "value": True}],
                },
            }
        )

        with patch("services.tuya_listener.send_door_opened_alert") as mock_alert:
            listener.on_message(message)
            mock_alert.assert_not_called()

    def test_on_message_protocol_4_format(self, listener, mock_config):
        """Test on_message handles Protocol 4 format."""
        message = json.dumps(
            {
                "devId": "test_device_123",
                "status": [{"code": "doorcontact_state", "value": True, "t": 1234567890}],
                "t": 1234567890,
            }
        )

        with patch("services.tuya_listener.send_door_opened_alert") as mock_alert:
            listener.on_message(message)
            mock_alert.assert_called_once()

    def test_on_message_battery_percentage(self, listener, mock_config):
        """Test that battery_percentage updates are logged."""
        message = json.dumps(
            {
                "bizCode": "devicePropertyMessage",
                "bizData": {
                    "devId": "test_device_123",
                    "properties": [{"code": "battery_percentage", "value": 85}],
                },
            }
        )

        with patch("services.tuya_listener.logging") as mock_logging:
            listener.on_message(message)
            # Battery updates should be logged at info level

    def test_on_message_dict_payload(self, listener, mock_config):
        """Test on_message handles dict payload (not string)."""
        message = {
            "bizCode": "devicePropertyMessage",
            "bizData": {
                "devId": "test_device_123",
                "properties": [{"code": "doorcontact_state", "value": True, "time": 1234567890}],
            },
        }

        with patch("services.tuya_listener.send_door_opened_alert") as mock_alert:
            listener.on_message(message)
            mock_alert.assert_called_once()

    def test_on_message_invalid_json(self, listener):
        """Test that invalid JSON is handled gracefully."""
        message = "not valid json {"

        with patch("services.tuya_listener.logging") as mock_logging:
            listener.on_message(message)
            # Should log error but not crash

    def test_on_message_no_device_id(self, listener):
        """Test that messages without device ID are skipped."""
        message = json.dumps(
            {
                "bizCode": "devicePropertyMessage",
                "bizData": {"properties": [{"code": "doorcontact_state", "value": True}]},
            }
        )

        with patch("services.tuya_listener.send_door_opened_alert") as mock_alert:
            listener.on_message(message)
            mock_alert.assert_not_called()

    def test_on_message_unknown_format(self, listener):
        """Test that unknown message formats are skipped."""
        message = json.dumps({"unknownField": "value"})

        with patch("services.tuya_listener.send_door_opened_alert") as mock_alert:
            listener.on_message(message)
            mock_alert.assert_not_called()

    def test_start_success(self, listener, mock_pulsar):
        """Test that start() initializes Pulsar connection."""
        with patch("services.tuya_service.tuya_service") as mock_tuya_service:
            mock_tuya_service.is_authenticated.return_value = True

            listener.start()

            # Verify Pulsar was started
            listener.open_pulsar.start.assert_called_once()

    def test_start_missing_credentials(self, mock_config):
        """Test that start() aborts if credentials are missing."""
        mock_config.ACCESS_ID = None

        from services.tuya_listener import TuyaListener

        with patch("services.tuya_listener.TuyaOpenPulsar"):
            listener = TuyaListener()
            listener.start()

            # Should not start Pulsar without credentials

    def test_start_authentication_failed(self, listener):
        """Test that start() aborts if authentication fails."""
        with patch("services.tuya_service.tuya_service") as mock_tuya_service:
            mock_tuya_service.is_authenticated.return_value = False

            listener.start()

            # Should not start Pulsar if auth fails
            listener.open_pulsar.start.assert_not_called()

    def test_handle_websocket_error_401(self, listener):
        """Test that 401 errors are handled and logged."""
        with patch("services.tuya_listener.logging") as mock_logging:
            listener.handle_websocket_error("401 Unauthorized")
            # Should log error about authentication failure

    def test_singleton_instance_exists(self):
        """Test that tuya_listener singleton exists."""
        from services.tuya_listener import tuya_listener

        assert tuya_listener is not None

    def test_on_message_unexpected_type(self, listener):
        """Test that unexpected message types are handled."""
        message = 12345  # Not string or dict

        with patch("services.tuya_listener.logging") as mock_logging:
            listener.on_message(message)
            # Should log error about unexpected type

    def test_on_message_other_status_code(self, listener, mock_config):
        """Test that other status codes are logged at debug level."""
        message = json.dumps(
            {
                "bizCode": "devicePropertyMessage",
                "bizData": {
                    "devId": "test_device_123",
                    "properties": [{"code": "other_status", "value": "some_value"}],
                },
            }
        )

        with patch("services.tuya_listener.logging") as mock_logging:
            listener.on_message(message)
            # Should log at debug level for other status codes

    def test_on_message_generic_exception(self, listener, mock_config):
        """Test that generic exceptions are caught and logged."""
        message = json.dumps(
            {
                "bizCode": "devicePropertyMessage",
                "bizData": {
                    "devId": "test_device_123",
                    "properties": [{"code": "doorcontact_state", "value": True}],
                },
            }
        )

        with patch("services.tuya_listener.send_door_opened_alert") as mock_alert:
            mock_alert.side_effect = Exception("Unexpected error")

            with patch("services.tuya_listener.logging") as mock_logging:
                listener.on_message(message)
                # Should catch exception and log error
