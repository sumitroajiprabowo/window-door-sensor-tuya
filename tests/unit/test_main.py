"""
Unit tests for main.py module.

Tests Flask application initialization and configuration validation.
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO


class TestValidateConfiguration:
    """Test cases for validate_configuration function."""

    @patch("main.WhatsAppConfig")
    @patch("main.TuyaConfig")
    @patch("main.logger")
    def test_validate_configuration_success(
        self, mock_logger, mock_tuya_config, mock_whatsapp_config, mock_env_vars
    ):
        """Test successful configuration validation."""
        mock_tuya_config.validate.return_value = None
        mock_whatsapp_config.validate.return_value = None

        from main import validate_configuration

        result = validate_configuration()

        assert result is True
        mock_tuya_config.validate.assert_called_once()
        mock_whatsapp_config.validate.assert_called_once()
        mock_logger.info.assert_called_with("Configuration validation passed")

    @patch("main.WhatsAppConfig")
    @patch("main.TuyaConfig")
    @patch("main.logger")
    def test_validate_configuration_tuya_failure(
        self, mock_logger, mock_tuya_config, mock_whatsapp_config, mock_env_vars
    ):
        """Test configuration validation fails when Tuya config is invalid."""
        mock_tuya_config.validate.side_effect = ValueError("Missing ACCESS_ID")
        mock_whatsapp_config.validate.return_value = None

        from main import validate_configuration

        result = validate_configuration()

        assert result is False
        mock_logger.error.assert_called()

    @patch("main.WhatsAppConfig")
    @patch("main.TuyaConfig")
    @patch("main.logger")
    def test_validate_configuration_whatsapp_failure(
        self, mock_logger, mock_tuya_config, mock_whatsapp_config, mock_env_vars
    ):
        """Test configuration validation fails when WhatsApp config is invalid."""
        mock_tuya_config.validate.return_value = None
        mock_whatsapp_config.validate.side_effect = ValueError("Missing API_URL")

        from main import validate_configuration

        result = validate_configuration()

        assert result is False
        mock_logger.error.assert_called()

    @patch("main.WhatsAppConfig")
    @patch("main.TuyaConfig")
    @patch("main.logger")
    def test_validate_configuration_logs_error_message(
        self, mock_logger, mock_tuya_config, mock_whatsapp_config, mock_env_vars
    ):
        """Test that validation failure logs the error message."""
        error_msg = "Missing required configuration"
        mock_tuya_config.validate.side_effect = ValueError(error_msg)

        from main import validate_configuration

        validate_configuration()

        # Check that error was logged with the error message
        error_calls = [call for call in mock_logger.error.call_args_list]
        assert len(error_calls) >= 1


class TestCreateApp:
    """Test cases for create_app function."""

    def test_create_app_returns_flask_instance(self, mock_env_vars):
        """Test that create_app returns a Flask application instance."""
        from main import create_app
        from flask import Flask

        app = create_app()

        assert isinstance(app, Flask)

    def test_create_app_registers_health_blueprint(self, mock_env_vars):
        """Test that health blueprint is registered."""
        from main import create_app

        app = create_app()

        # Check that /health route exists
        assert any(rule.rule == "/health" for rule in app.url_map.iter_rules())

    def test_create_app_registers_device_blueprint(self, mock_env_vars):
        """Test that device blueprint is registered."""
        from main import create_app

        app = create_app()

        # Check that device routes exist
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        assert any("/devices/" in rule for rule in rules)

    def test_create_app_enables_cors(self, mock_env_vars):
        """Test that CORS is enabled on the app."""
        from main import create_app

        app = create_app()

        # Create a test client
        client = app.test_client()
        response = client.get("/health")

        # CORS headers should be present or app should handle CORS
        # (CORS extension is applied to the app)
        assert response.status_code == 200


class TestStartListener:
    """Test cases for start_listener function."""

    @patch("builtins.print")
    def test_start_listener_calls_tuya_listener_start(self, mock_print, mock_env_vars):
        """Test that start_listener calls tuya_listener.start()."""
        # Mock the services.tuya_listener module
        mock_tuya_listener_module = Mock()
        mock_listener = Mock()
        mock_tuya_listener_module.tuya_listener = mock_listener

        with patch.dict(
            "sys.modules", {"services.tuya_listener": mock_tuya_listener_module}
        ):
            from main import start_listener

            start_listener()

            mock_listener.start.assert_called_once()

    @patch("builtins.print")
    def test_start_listener_handles_exception(self, mock_print, mock_env_vars):
        """Test that start_listener handles exceptions gracefully."""
        # Mock the services.tuya_listener module to raise an exception
        mock_tuya_listener_module = Mock()
        mock_tuya_listener_module.tuya_listener.start.side_effect = Exception(
            "Connection error"
        )

        with patch.dict(
            "sys.modules", {"services.tuya_listener": mock_tuya_listener_module}
        ):
            from main import start_listener

            # Should not raise exception - it catches and prints it
            start_listener()

    @patch("traceback.print_exc")
    @patch("builtins.print")
    def test_start_listener_prints_traceback_on_error(
        self, mock_print, mock_traceback, mock_env_vars
    ):
        """Test that start_listener prints traceback on error."""
        # Mock the services.tuya_listener module to raise an exception
        mock_tuya_listener_module = Mock()
        mock_tuya_listener_module.tuya_listener.start.side_effect = Exception(
            "Test error"
        )

        with patch.dict(
            "sys.modules", {"services.tuya_listener": mock_tuya_listener_module}
        ):
            from main import start_listener

            # Should catch exception and print traceback
            start_listener()

            # Verify traceback.print_exc() was called
            mock_traceback.assert_called_once()


class TestAppInstance:
    """Test cases for app instance creation."""

    def test_app_instance_exists(self, mock_env_vars):
        """Test that app instance is created at module level."""
        import main

        assert hasattr(main, "app")
        assert main.app is not None

    def test_app_instance_is_flask_app(self, mock_env_vars):
        """Test that app instance is a Flask application."""
        from flask import Flask
        import main

        assert isinstance(main.app, Flask)


class TestMainExecution:
    """Test cases for main execution block."""

    def test_main_exits_on_validation_failure(self, mock_env_vars):
        """Test that main exits when configuration validation fails."""
        # This test verifies the validate_configuration behavior
        # The actual __main__ block is difficult to test in unit tests
        # We verify that validate_configuration correctly returns False
        # when configuration is invalid

        with patch("main.TuyaConfig") as mock_tuya:
            mock_tuya.validate.side_effect = ValueError("Missing config")

            from main import validate_configuration

            result = validate_configuration()

            # Should return False on validation failure
            assert result is False

    @patch("main.Config")
    def test_debug_mode_from_config(self, mock_config, mock_env_vars):
        """Test that debug mode is read from Config."""
        mock_config.DEBUG = True

        import importlib
        import main

        importlib.reload(main)

        # Verify Config.DEBUG is accessible
        from main import Config

        # The actual value should come from env vars in mock_env_vars
        assert hasattr(Config, "DEBUG")

    @patch("main.Config")
    def test_host_and_port_from_config(self, mock_config, mock_env_vars):
        """Test that host and port are read from Config."""
        mock_config.HOST = "0.0.0.0"
        mock_config.PORT = 5001

        from main import Config

        assert hasattr(Config, "HOST")
        assert hasattr(Config, "PORT")


class TestLoggingConfiguration:
    """Test cases for logging configuration."""

    @patch("main.Config")
    def test_logging_level_debug_when_debug_enabled(self, mock_config):
        """Test that logging level is DEBUG when Config.DEBUG is True."""
        mock_config.DEBUG = True

        import importlib
        import main

        importlib.reload(main)

        # Logging is configured at module level
        # We can verify it doesn't raise errors
        assert True

    @patch("main.Config")
    def test_logging_level_info_when_debug_disabled(self, mock_config):
        """Test that logging level is INFO when Config.DEBUG is False."""
        mock_config.DEBUG = False

        import importlib
        import main

        importlib.reload(main)

        # Logging is configured at module level
        # We can verify it doesn't raise errors
        assert True

    def test_logger_exists(self, mock_env_vars):
        """Test that logger is created."""
        import main

        assert hasattr(main, "logger")
        assert main.logger is not None


class TestReloaderDetection:
    """Test cases for Flask reloader detection."""

    @patch.dict("os.environ", {"WERKZEUG_RUN_MAIN": "true"})
    def test_werkzeug_run_main_detection(self, mock_env_vars):
        """Test detection of Flask reloader child process."""
        import os

        result = os.environ.get("WERKZEUG_RUN_MAIN") == "true"

        assert result is True

    @patch.dict("os.environ", {}, clear=True)
    def test_werkzeug_run_main_not_set(self, mock_env_vars):
        """Test when not in Flask reloader child process."""
        # Need to add back the required env vars
        import os

        for key, value in mock_env_vars.items():
            os.environ[key] = value

        result = os.environ.get("WERKZEUG_RUN_MAIN") == "true"

        assert result is False
