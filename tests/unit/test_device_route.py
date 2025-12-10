"""
Unit tests for routes/device.py module.

Tests device management API endpoints.
"""

import pytest
import json
from unittest.mock import Mock, patch


class TestGetDeviceStatus:
    """Test cases for GET /devices/<device_id>/status endpoint."""

    @patch("routes.device.tuya_service")
    def test_get_device_status_success(self, mock_tuya_service, flask_test_client):
        """Test successful device status retrieval."""
        mock_tuya_service.get_device_status.return_value = {
            "success": True,
            "result": [
                {"code": "doorcontact_state", "value": False},
                {"code": "battery_percentage", "value": 85},
            ],
            "msg": "success",
            "code": 200,
        }

        response = flask_test_client.get("/devices/test_device_123/status")

        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data["status"] == "success"
        assert len(data["result"]) == 2

    @patch("routes.device.tuya_service")
    def test_get_device_status_calls_service_with_device_id(
        self, mock_tuya_service, flask_test_client
    ):
        """Test that service is called with correct device ID."""
        mock_tuya_service.get_device_status.return_value = {
            "success": True,
            "result": [],
            "msg": "success",
        }

        device_id = "test_device_456"
        flask_test_client.get(f"/devices/{device_id}/status")

        mock_tuya_service.get_device_status.assert_called_once_with(device_id)

    @patch("routes.device.tuya_service")
    def test_get_device_status_api_failure(self, mock_tuya_service, flask_test_client):
        """Test handling of API failure response."""
        mock_tuya_service.get_device_status.return_value = {
            "success": False,
            "result": None,
            "msg": "Device not found",
            "code": 404,
        }

        response = flask_test_client.get("/devices/invalid_device/status")

        assert response.status_code == 404
        data = json.loads(response.get_data(as_text=True))
        assert data["status"] == "error"
        assert data["message"] == "Device not found"

    @patch("routes.device.tuya_service")
    def test_get_device_status_exception(self, mock_tuya_service, flask_test_client):
        """Test handling of unexpected exceptions."""
        mock_tuya_service.get_device_status.side_effect = Exception("Connection error")

        response = flask_test_client.get("/devices/test_device/status")

        assert response.status_code == 500
        data = json.loads(response.get_data(as_text=True))
        assert data["status"] == "error"
        assert data["message"] == "Internal Server Error"

    @patch("routes.device.tuya_service")
    def test_get_device_status_door_open(self, mock_tuya_service, flask_test_client):
        """Test device status when door is open."""
        mock_tuya_service.get_device_status.return_value = {
            "success": True,
            "result": [
                {"code": "doorcontact_state", "value": True},
                {"code": "battery_percentage", "value": 90},
            ],
        }

        response = flask_test_client.get("/devices/test_device/status")
        data = json.loads(response.get_data(as_text=True))

        assert data["result"][0]["value"] is True  # Door is open

    @patch("routes.device.tuya_service")
    def test_get_device_status_door_closed(self, mock_tuya_service, flask_test_client):
        """Test device status when door is closed."""
        mock_tuya_service.get_device_status.return_value = {
            "success": True,
            "result": [{"code": "doorcontact_state", "value": False}],
        }

        response = flask_test_client.get("/devices/test_device/status")
        data = json.loads(response.get_data(as_text=True))

        assert data["result"][0]["value"] is False  # Door is closed

    @patch("routes.device.tuya_service")
    def test_get_device_status_missing_msg(self, mock_tuya_service, flask_test_client):
        """Test handling when API response is missing msg field."""
        mock_tuya_service.get_device_status.return_value = {
            "success": False,
            "result": None,
            "code": 500,
        }

        response = flask_test_client.get("/devices/test_device/status")
        data = json.loads(response.get_data(as_text=True))

        assert data["message"] == "Failed to fetch status"

    @patch("routes.device.tuya_service")
    def test_get_device_status_missing_code(self, mock_tuya_service, flask_test_client):
        """Test handling when API response is missing code field."""
        mock_tuya_service.get_device_status.return_value = {
            "success": False,
            "result": None,
            "msg": "Error",
        }

        response = flask_test_client.get("/devices/test_device/status")

        assert response.status_code == 500


class TestSendDeviceCommand:
    """Test cases for POST /devices/<device_id>/commands endpoint."""

    @patch("routes.device.tuya_service")
    def test_send_device_command_success(self, mock_tuya_service, flask_test_client):
        """Test successful command sending."""
        mock_tuya_service.send_command.return_value = {
            "success": True,
            "result": {"status": "ok"},
            "msg": "success",
        }

        commands = [{"code": "switch", "value": True}]
        response = flask_test_client.post(
            "/devices/test_device/commands",
            json={"commands": commands},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = json.loads(response.get_data(as_text=True))
        assert data["status"] == "success"
        assert data["message"] == "Command sent successfully"

    @patch("routes.device.tuya_service")
    def test_send_device_command_calls_service(
        self, mock_tuya_service, flask_test_client
    ):
        """Test that service is called with correct parameters."""
        mock_tuya_service.send_command.return_value = {"success": True, "result": {}}

        device_id = "test_device_789"
        commands = [{"code": "brightness", "value": 75}]

        flask_test_client.post(
            f"/devices/{device_id}/commands",
            json={"commands": commands},
            content_type="application/json",
        )

        mock_tuya_service.send_command.assert_called_once_with(device_id, commands)

    def test_send_device_command_missing_body(self, flask_test_client):
        """Test handling of missing request body."""
        response = flask_test_client.post(
            "/devices/test_device/commands", content_type="application/json"
        )

        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))
        assert data["status"] == "error"
        assert data["message"] == "Invalid request body"

    def test_send_device_command_missing_commands_field(self, flask_test_client):
        """Test handling of request body without commands field."""
        response = flask_test_client.post(
            "/devices/test_device/commands",
            json={"invalid": "data"},
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))
        assert data["status"] == "error"
        assert data["message"] == "Invalid request body"

    @patch("routes.device.tuya_service")
    def test_send_device_command_api_failure(
        self, mock_tuya_service, flask_test_client
    ):
        """Test handling of API failure response."""
        mock_tuya_service.send_command.return_value = {
            "success": False,
            "result": None,
            "msg": "Command failed",
            "code": 400,
        }

        commands = [{"code": "switch", "value": True}]
        response = flask_test_client.post(
            "/devices/test_device/commands",
            json={"commands": commands},
            content_type="application/json",
        )

        assert response.status_code == 400
        data = json.loads(response.get_data(as_text=True))
        assert data["status"] == "error"
        assert data["message"] == "Command failed"

    @patch("routes.device.tuya_service")
    def test_send_device_command_exception(self, mock_tuya_service, flask_test_client):
        """Test handling of unexpected exceptions."""
        mock_tuya_service.send_command.side_effect = Exception("Network error")

        commands = [{"code": "switch", "value": True}]
        response = flask_test_client.post(
            "/devices/test_device/commands",
            json={"commands": commands},
            content_type="application/json",
        )

        assert response.status_code == 500
        data = json.loads(response.get_data(as_text=True))
        assert data["status"] == "error"
        assert data["message"] == "Internal Server Error"

    @patch("routes.device.tuya_service")
    def test_send_device_command_multiple_commands(
        self, mock_tuya_service, flask_test_client
    ):
        """Test sending multiple commands at once."""
        mock_tuya_service.send_command.return_value = {"success": True, "result": {}}

        commands = [
            {"code": "switch", "value": True},
            {"code": "brightness", "value": 50},
            {"code": "color", "value": "blue"},
        ]
        response = flask_test_client.post(
            "/devices/test_device/commands",
            json={"commands": commands},
            content_type="application/json",
        )

        assert response.status_code == 200
        mock_tuya_service.send_command.assert_called_once_with("test_device", commands)

    @patch("routes.device.tuya_service")
    def test_send_device_command_empty_commands(
        self, mock_tuya_service, flask_test_client
    ):
        """Test sending empty commands list."""
        mock_tuya_service.send_command.return_value = {"success": True, "result": {}}

        response = flask_test_client.post(
            "/devices/test_device/commands",
            json={"commands": []},
            content_type="application/json",
        )

        # Should still be valid even with empty list
        assert response.status_code == 200

    @patch("routes.device.tuya_service")
    def test_send_device_command_missing_msg(
        self, mock_tuya_service, flask_test_client
    ):
        """Test handling when API response is missing msg field."""
        mock_tuya_service.send_command.return_value = {
            "success": False,
            "result": None,
            "code": 500,
        }

        commands = [{"code": "switch", "value": True}]
        response = flask_test_client.post(
            "/devices/test_device/commands",
            json={"commands": commands},
            content_type="application/json",
        )

        data = json.loads(response.get_data(as_text=True))
        assert data["message"] == "Failed to send command"

    @patch("routes.device.tuya_service")
    def test_send_device_command_missing_code(
        self, mock_tuya_service, flask_test_client
    ):
        """Test handling when API response is missing code field."""
        mock_tuya_service.send_command.return_value = {
            "success": False,
            "result": None,
            "msg": "Error",
        }

        commands = [{"code": "switch", "value": True}]
        response = flask_test_client.post(
            "/devices/test_device/commands",
            json={"commands": commands},
            content_type="application/json",
        )

        assert response.status_code == 500
