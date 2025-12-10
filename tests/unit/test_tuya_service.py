"""
Unit tests for services/tuya_service.py module.

Tests Tuya Cloud API integration service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestTuyaServiceInit:
    """Test cases for TuyaService initialization."""

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_tuya_service_init_creates_openapi_instance(self, mock_tuya_api, mock_env_vars):
        """Test that TuyaService creates TuyaOpenAPI instance on init."""
        from services.tuya_service import TuyaService
        from config.Config import TuyaConfig

        service = TuyaService()

        mock_tuya_api.assert_called_once_with(
            TuyaConfig.API_ENDPOINT, TuyaConfig.ACCESS_ID, TuyaConfig.ACCESS_SECRET
        )

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_tuya_service_init_calls_connect(self, mock_tuya_api, mock_env_vars):
        """Test that TuyaService calls connect() during initialization."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.is_connect.return_value = False

        from services.tuya_service import TuyaService

        service = TuyaService()

        mock_instance.connect.assert_called_once()


class TestTuyaServiceConnect:
    """Test cases for TuyaService.connect() method."""

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_connect_when_not_connected(self, mock_tuya_api, mock_env_vars):
        """Test connect() establishes connection when not connected."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.is_connect.return_value = False

        from services.tuya_service import TuyaService

        service = TuyaService()
        mock_instance.connect.reset_mock()  # Reset the call from __init__
        service.connect()

        mock_instance.connect.assert_called_once()

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_connect_when_already_connected(self, mock_tuya_api, mock_env_vars):
        """Test connect() does nothing when already connected."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.is_connect.return_value = True

        from services.tuya_service import TuyaService

        service = TuyaService()
        mock_instance.connect.reset_mock()
        service.connect()

        # Should not call connect again if already connected
        mock_instance.connect.assert_not_called()

    @patch("services.tuya_service.TuyaOpenAPI")
    @patch("services.tuya_service.logging")
    def test_connect_logs_success(self, mock_logging, mock_tuya_api, mock_env_vars):
        """Test connect() logs success message."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.is_connect.return_value = False

        from services.tuya_service import TuyaService

        service = TuyaService()

        mock_logging.info.assert_called_with("Connected to Tuya Cloud")

    @patch("services.tuya_service.TuyaOpenAPI")
    @patch("services.tuya_service.logging")
    def test_connect_handles_exception(self, mock_logging, mock_tuya_api, mock_env_vars):
        """Test connect() handles exceptions gracefully."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.is_connect.return_value = False
        mock_instance.connect.side_effect = Exception("Connection failed")

        from services.tuya_service import TuyaService

        service = TuyaService()
        mock_instance.connect.reset_mock()
        mock_instance.connect.side_effect = Exception("Connection failed")

        # Should not raise exception
        service.connect()

        mock_logging.error.assert_called()


class TestTuyaServiceIsAuthenticated:
    """Test cases for TuyaService.is_authenticated() method."""

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_is_authenticated_returns_true_when_connected(self, mock_tuya_api, mock_env_vars):
        """Test is_authenticated returns True when properly connected."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.access_id = "valid_access_id"
        mock_instance.is_connect.return_value = True

        from services.tuya_service import TuyaService

        service = TuyaService()
        result = service.is_authenticated()

        assert result is True

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_is_authenticated_returns_false_with_placeholder_credentials(
        self, mock_tuya_api, mock_env_vars
    ):
        """Test is_authenticated returns False with placeholder access_id."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.access_id = "your_access_id"
        mock_instance.is_connect.return_value = True

        from services.tuya_service import TuyaService

        service = TuyaService()
        result = service.is_authenticated()

        assert result is False

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_is_authenticated_returns_false_when_not_connected(self, mock_tuya_api, mock_env_vars):
        """Test is_authenticated returns False when not connected."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.access_id = "valid_access_id"
        mock_instance.is_connect.return_value = False

        from services.tuya_service import TuyaService

        service = TuyaService()
        result = service.is_authenticated()

        assert result is False

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_is_authenticated_returns_false_with_empty_access_id(
        self, mock_tuya_api, mock_env_vars
    ):
        """Test is_authenticated returns False with empty access_id."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.access_id = ""
        mock_instance.is_connect.return_value = True

        from services.tuya_service import TuyaService

        service = TuyaService()
        result = service.is_authenticated()

        assert result is False

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_is_authenticated_returns_false_with_none_access_id(self, mock_tuya_api, mock_env_vars):
        """Test is_authenticated returns False with None access_id."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.access_id = None
        mock_instance.is_connect.return_value = True

        from services.tuya_service import TuyaService

        service = TuyaService()
        result = service.is_authenticated()

        assert result is False


class TestTuyaServiceGetDeviceStatus:
    """Test cases for TuyaService.get_device_status() method."""

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_get_device_status_calls_connect(self, mock_tuya_api, mock_env_vars):
        """Test get_device_status calls connect before making API call."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.is_connect.return_value = True
        mock_instance.get.return_value = {"success": True, "result": []}

        from services.tuya_service import TuyaService

        service = TuyaService()
        mock_instance.connect.reset_mock()
        mock_instance.is_connect.return_value = False
        service.get_device_status("test_device")

        mock_instance.connect.assert_called_once()

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_get_device_status_makes_correct_api_call(self, mock_tuya_api, mock_env_vars):
        """Test get_device_status makes correct API call."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.is_connect.return_value = True
        mock_instance.get.return_value = {"success": True, "result": []}

        from services.tuya_service import TuyaService

        device_id = "device_123"
        service = TuyaService()
        service.get_device_status(device_id)

        mock_instance.get.assert_called_once_with(f"/v1.0/devices/{device_id}/status")

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_get_device_status_returns_response(self, mock_tuya_api, mock_env_vars):
        """Test get_device_status returns API response."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.is_connect.return_value = True

        expected_response = {
            "success": True,
            "result": [
                {"code": "doorcontact_state", "value": False},
                {"code": "battery_percentage", "value": 85},
            ],
        }
        mock_instance.get.return_value = expected_response

        from services.tuya_service import TuyaService

        service = TuyaService()
        result = service.get_device_status("test_device")

        assert result == expected_response


class TestTuyaServiceSendCommand:
    """Test cases for TuyaService.send_command() method."""

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_send_command_calls_connect(self, mock_tuya_api, mock_env_vars):
        """Test send_command calls connect before making API call."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.is_connect.return_value = True
        mock_instance.post.return_value = {"success": True}

        from services.tuya_service import TuyaService

        service = TuyaService()
        mock_instance.connect.reset_mock()
        mock_instance.is_connect.return_value = False
        service.send_command("test_device", [])

        mock_instance.connect.assert_called_once()

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_send_command_makes_correct_api_call(self, mock_tuya_api, mock_env_vars):
        """Test send_command makes correct API call."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.is_connect.return_value = True
        mock_instance.post.return_value = {"success": True}

        from services.tuya_service import TuyaService

        device_id = "device_456"
        commands = [{"code": "switch", "value": True}]
        service = TuyaService()
        service.send_command(device_id, commands)

        mock_instance.post.assert_called_once_with(
            f"/v1.0/devices/{device_id}/commands", {"commands": commands}
        )

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_send_command_returns_response(self, mock_tuya_api, mock_env_vars):
        """Test send_command returns API response."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.is_connect.return_value = True

        expected_response = {"success": True, "result": {"status": "ok"}}
        mock_instance.post.return_value = expected_response

        from services.tuya_service import TuyaService

        service = TuyaService()
        result = service.send_command("test_device", [{"code": "test", "value": 1}])

        assert result == expected_response

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_send_command_with_multiple_commands(self, mock_tuya_api, mock_env_vars):
        """Test send_command with multiple commands."""
        mock_instance = Mock()
        mock_tuya_api.return_value = mock_instance
        mock_instance.is_connect.return_value = True
        mock_instance.post.return_value = {"success": True}

        from services.tuya_service import TuyaService

        commands = [{"code": "switch", "value": True}, {"code": "brightness", "value": 75}]
        service = TuyaService()
        service.send_command("test_device", commands)

        call_args = mock_instance.post.call_args
        assert call_args[0][1]["commands"] == commands


class TestTuyaServiceSingleton:
    """Test cases for tuya_service singleton instance."""

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_tuya_service_singleton_exists(self, mock_tuya_api, mock_env_vars):
        """Test that tuya_service singleton instance is created."""
        from services import tuya_service

        assert hasattr(tuya_service, "tuya_service")
        assert tuya_service.tuya_service is not None

    @patch("services.tuya_service.TuyaOpenAPI")
    def test_tuya_service_singleton_is_tuya_service_instance(self, mock_tuya_api, mock_env_vars):
        """Test that tuya_service is an instance of TuyaService."""
        from services.tuya_service import tuya_service, TuyaService

        assert isinstance(tuya_service, TuyaService)
