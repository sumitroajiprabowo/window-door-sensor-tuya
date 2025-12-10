"""
Unit tests for services/whatsapp_service.py module.

Tests WhatsApp notification service functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests


class TestSendWhatsAppMessage:
    """Test cases for send_whatsapp_message function."""

    @patch("services.whatsapp_service.requests.post")
    def test_send_whatsapp_message_success(self, mock_post, mock_env_vars):
        """Test successful WhatsApp message sending."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        from services.whatsapp_service import send_whatsapp_message

        result = send_whatsapp_message("Test message")

        assert result is True
        mock_post.assert_called_once()

    @patch("services.whatsapp_service.requests.post")
    def test_send_whatsapp_message_calls_api_with_correct_url(
        self, mock_post, mock_env_vars
    ):
        """Test that API is called with correct URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        from services.whatsapp_service import send_whatsapp_message
        from config.Config import WhatsAppConfig

        send_whatsapp_message("Test message")

        call_args = mock_post.call_args
        assert call_args[0][0] == WhatsAppConfig.API_URL

    @patch("services.whatsapp_service.requests.post")
    def test_send_whatsapp_message_includes_auth(self, mock_post, mock_env_vars):
        """Test that request includes HTTP Basic authentication."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        from services.whatsapp_service import send_whatsapp_message
        from config.Config import WhatsAppConfig

        send_whatsapp_message("Test message")

        call_args, call_kwargs = mock_post.call_args
        auth = call_kwargs["auth"]
        assert auth.username == WhatsAppConfig.API_USER
        assert auth.password == WhatsAppConfig.API_PASSWORD

    @patch("services.whatsapp_service.requests.post")
    def test_send_whatsapp_message_includes_correct_headers(
        self, mock_post, mock_env_vars
    ):
        """Test that request includes correct headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        from services.whatsapp_service import send_whatsapp_message

        send_whatsapp_message("Test message")

        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["headers"]["Content-Type"] == "application/json"

    @patch("services.whatsapp_service.requests.post")
    def test_send_whatsapp_message_includes_correct_payload(
        self, mock_post, mock_env_vars
    ):
        """Test that request includes correct payload."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        from services.whatsapp_service import send_whatsapp_message
        from config.Config import WhatsAppConfig

        test_message = "Test notification"
        send_whatsapp_message(test_message)

        call_kwargs = mock_post.call_args[1]
        payload = call_kwargs["json"]

        assert payload["phone"] == WhatsAppConfig.GROUP_ID
        assert payload["message"] == test_message
        # is_forwarded and duration are conditional based on config
        # They should not be in payload with default test configuration

    @patch("services.whatsapp_service.requests.post")
    def test_send_whatsapp_message_includes_timeout(self, mock_post, mock_env_vars):
        """Test that request includes timeout parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        from services.whatsapp_service import send_whatsapp_message

        send_whatsapp_message("Test message")

        call_kwargs = mock_post.call_args[1]
        assert call_kwargs["timeout"] == 10

    @patch("services.whatsapp_service.requests.post")
    @patch("services.whatsapp_service.logging")
    def test_send_whatsapp_message_logs_info(
        self, mock_logging, mock_post, mock_env_vars
    ):
        """Test that function logs message sending."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        from services.whatsapp_service import send_whatsapp_message

        test_message = "Log test message"
        send_whatsapp_message(test_message)

        # Verify info log was called
        mock_logging.info.assert_called()

    @patch("services.whatsapp_service.requests.post")
    def test_send_whatsapp_message_request_exception(self, mock_post, mock_env_vars):
        """Test handling of request exception."""
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")

        from services.whatsapp_service import send_whatsapp_message

        result = send_whatsapp_message("Test message")

        assert result is False

    @patch("services.whatsapp_service.requests.post")
    @patch("services.whatsapp_service.logging")
    def test_send_whatsapp_message_logs_error_on_exception(
        self, mock_logging, mock_post, mock_env_vars
    ):
        """Test that function logs error on exception."""
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")

        from services.whatsapp_service import send_whatsapp_message

        send_whatsapp_message("Test message")

        mock_logging.error.assert_called()

    @patch("services.whatsapp_service.requests.post")
    def test_send_whatsapp_message_http_error(self, mock_post, mock_env_vars):
        """Test handling of HTTP error response."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Bad Request"
        )
        mock_post.return_value = mock_response

        from services.whatsapp_service import send_whatsapp_message

        result = send_whatsapp_message("Test message")

        assert result is False

    @patch("services.whatsapp_service.requests.post")
    @patch("services.whatsapp_service.logging")
    def test_send_whatsapp_message_logs_response_on_error(
        self, mock_logging, mock_post, mock_env_vars
    ):
        """Test that function logs response text on error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Error details"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Bad Request"
        )
        mock_response.raise_for_status.side_effect.response = mock_response
        mock_post.return_value = mock_response

        from services.whatsapp_service import send_whatsapp_message

        send_whatsapp_message("Test message")

        # Verify error logging was called
        assert mock_logging.error.call_count >= 1

    @patch("services.whatsapp_service.requests.post")
    def test_send_whatsapp_message_timeout_exception(self, mock_post, mock_env_vars):
        """Test handling of timeout exception."""
        mock_post.side_effect = requests.exceptions.Timeout("Request timeout")

        from services.whatsapp_service import send_whatsapp_message

        result = send_whatsapp_message("Test message")

        assert result is False

    @patch("services.whatsapp_service.requests.post")
    def test_send_whatsapp_message_connection_error(self, mock_post, mock_env_vars):
        """Test handling of connection error."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

        from services.whatsapp_service import send_whatsapp_message

        result = send_whatsapp_message("Test message")

        assert result is False


class TestSendDoorOpenedAlert:
    """Test cases for send_door_opened_alert function."""

    @patch("services.whatsapp_service.send_whatsapp_message")
    def test_send_door_opened_alert_calls_send_whatsapp_message(
        self, mock_send, mock_env_vars
    ):
        """Test that send_door_opened_alert calls send_whatsapp_message."""
        mock_send.return_value = True

        from services.whatsapp_service import send_door_opened_alert
        from config.Config import WhatsAppConfig

        send_door_opened_alert()

        mock_send.assert_called_once_with(WhatsAppConfig.MESSAGE_DOOR_OPENED)

    @patch("services.whatsapp_service.send_whatsapp_message")
    def test_send_door_opened_alert_returns_result(self, mock_send, mock_env_vars):
        """Test that send_door_opened_alert returns result from send_whatsapp_message."""
        mock_send.return_value = True

        from services.whatsapp_service import send_door_opened_alert

        result = send_door_opened_alert()

        assert result is True

    @patch("services.whatsapp_service.send_whatsapp_message")
    def test_send_door_opened_alert_returns_false_on_failure(
        self, mock_send, mock_env_vars
    ):
        """Test that send_door_opened_alert returns False on failure."""
        mock_send.return_value = False

        from services.whatsapp_service import send_door_opened_alert

        result = send_door_opened_alert()

        assert result is False


class TestSendDoorClosedAlert:
    """Test cases for send_door_closed_alert function."""

    @patch("services.whatsapp_service.send_whatsapp_message")
    def test_send_door_closed_alert_calls_send_whatsapp_message(
        self, mock_send, mock_env_vars
    ):
        """Test that send_door_closed_alert calls send_whatsapp_message."""
        mock_send.return_value = True

        from services.whatsapp_service import send_door_closed_alert
        from config.Config import WhatsAppConfig

        send_door_closed_alert()

        mock_send.assert_called_once_with(WhatsAppConfig.MESSAGE_DOOR_CLOSED)

    @patch("services.whatsapp_service.send_whatsapp_message")
    def test_send_door_closed_alert_returns_result(self, mock_send, mock_env_vars):
        """Test that send_door_closed_alert returns result from send_whatsapp_message."""
        mock_send.return_value = True

        from services.whatsapp_service import send_door_closed_alert

        result = send_door_closed_alert()

        assert result is True

    @patch("services.whatsapp_service.send_whatsapp_message")
    def test_send_door_closed_alert_returns_false_on_failure(
        self, mock_send, mock_env_vars
    ):
        """Test that send_door_closed_alert returns False on failure."""
        mock_send.return_value = False

        from services.whatsapp_service import send_door_closed_alert

        result = send_door_closed_alert()

        assert result is False
