"""
Unit tests for config/Config.py module.

Tests configuration loading, validation, and environment variable handling.
"""

import pytest
import os
from unittest.mock import patch


class TestConfig:
    """Test cases for Config class."""

    def test_default_port(self, mock_env_vars):
        """Test that default port is loaded correctly."""
        from config.Config import Config

        assert Config.PORT == 5001

    def test_custom_port(self, monkeypatch):
        """Test that custom port from environment is used."""
        monkeypatch.setenv("FLASK_PORT", "8080")

        # Reload the module to pick up new env var
        import importlib
        import config.Config

        importlib.reload(config.Config)

        assert config.Config.Config.PORT == 8080

    def test_debug_mode_false_by_default(self, monkeypatch):
        """Test that debug mode is False by default."""
        monkeypatch.setenv("FLASK_DEBUG", "False")

        import importlib
        import config.Config

        importlib.reload(config.Config)

        assert config.Config.Config.DEBUG is False

    def test_debug_mode_enabled(self, monkeypatch):
        """Test that debug mode can be enabled."""
        monkeypatch.setenv("FLASK_DEBUG", "True")

        import importlib
        import config.Config

        importlib.reload(config.Config)

        assert config.Config.Config.DEBUG is True

    def test_host_default_value(self, mock_env_vars):
        """Test that default host is 0.0.0.0."""
        from config.Config import Config

        assert Config.HOST == "0.0.0.0"

    def test_custom_host(self, monkeypatch):
        """Test that custom host from environment is used."""
        monkeypatch.setenv("FLASK_HOST", "localhost")

        import importlib
        import config.Config

        importlib.reload(config.Config)

        assert config.Config.Config.HOST == "localhost"

    def test_poll_interval_default(self, mock_env_vars):
        """Test that default poll interval is 2 seconds."""
        from config.Config import Config

        assert Config.POLL_INTERVAL == 2

    def test_custom_poll_interval(self, monkeypatch):
        """Test that custom poll interval from environment is used."""
        monkeypatch.setenv("POLL_INTERVAL", "5")

        import importlib
        import config.Config

        importlib.reload(config.Config)

        assert config.Config.Config.POLL_INTERVAL == 5

    def test_env_default_value(self, monkeypatch):
        """Test that default environment is production."""
        monkeypatch.delenv("ENV", raising=False)

        import importlib
        import config.Config

        importlib.reload(config.Config)

        assert config.Config.Config.ENV == "production"

    def test_custom_env(self, mock_env_vars):
        """Test that custom environment from environment variable is used."""
        from config.Config import Config

        assert Config.ENV == "test"


class TestTuyaConfig:
    """Test cases for TuyaConfig class."""

    def test_access_id_loaded(self, mock_env_vars):
        """Test that Tuya access ID is loaded from environment."""
        from config.Config import TuyaConfig

        assert TuyaConfig.ACCESS_ID == "test_access_id"

    def test_access_secret_loaded(self, mock_env_vars):
        """Test that Tuya access secret is loaded from environment."""
        from config.Config import TuyaConfig

        assert TuyaConfig.ACCESS_SECRET == "test_access_secret"

    def test_api_endpoint_loaded(self, mock_env_vars):
        """Test that Tuya API endpoint is loaded from environment."""
        from config.Config import TuyaConfig

        assert TuyaConfig.API_ENDPOINT == "https://openapi.tuyaus.com"

    def test_device_id_loaded(self, mock_env_vars):
        """Test that device ID is loaded from environment."""
        from config.Config import TuyaConfig

        assert TuyaConfig.DEVICE_ID == "test_device_id"

    def test_pulsar_endpoint_loaded(self, mock_env_vars):
        """Test that Pulsar endpoint is loaded from environment."""
        from config.Config import TuyaConfig

        assert TuyaConfig.TUYA_PULSAR_ENDPOINT == "wss://test.pulsar.com"

    def test_validate_success(self, mock_env_vars):
        """Test that validation passes with all required fields."""
        from config.Config import TuyaConfig

        # Should not raise any exception
        TuyaConfig.validate()

    def test_validate_missing_access_id(self, monkeypatch):
        """Test that validation fails when ACCESS_ID is missing."""
        # Mock os.getenv to return None for TUYA_ACCESS_ID but return values for others
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key == "TUYA_ACCESS_ID":
                return None
            elif key == "TUYA_ACCESS_SECRET":
                return "test_secret"
            elif key == "TUYA_ENDPOINT":
                return "https://test.com"
            elif key == "DEVICE_ID":
                return "test_device"
            return original_getenv(key, default)

        with patch("os.getenv", side_effect=mock_getenv):
            import importlib
            import config.Config as config_module

            reloaded = importlib.reload(config_module)

            with pytest.raises(ValueError) as exc_info:
                reloaded.TuyaConfig.validate()

            assert "ACCESS_ID" in str(exc_info.value)

    def test_validate_missing_access_secret(self, monkeypatch):
        """Test that validation fails when ACCESS_SECRET is missing."""
        # Mock os.getenv to return None for TUYA_ACCESS_SECRET
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key == "TUYA_ACCESS_SECRET":
                return None
            elif key == "TUYA_ACCESS_ID":
                return "test_id"
            elif key == "TUYA_ENDPOINT":
                return "https://test.com"
            elif key == "DEVICE_ID":
                return "test_device"
            return original_getenv(key, default)

        with patch("os.getenv", side_effect=mock_getenv):
            import importlib
            import config.Config as config_module

            reloaded = importlib.reload(config_module)

            with pytest.raises(ValueError) as exc_info:
                reloaded.TuyaConfig.validate()

            assert "ACCESS_SECRET" in str(exc_info.value)

    def test_validate_missing_api_endpoint(self, monkeypatch):
        """Test that validation fails when API_ENDPOINT is missing."""
        # Mock os.getenv to return None for TUYA_ENDPOINT but return values for others
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key == "TUYA_ENDPOINT":
                return None
            elif key == "TUYA_ACCESS_ID":
                return "test_id"
            elif key == "TUYA_ACCESS_SECRET":
                return "test_secret"
            elif key == "DEVICE_ID":
                return "test_device"
            return original_getenv(key, default)

        with patch("os.getenv", side_effect=mock_getenv):
            import importlib
            import config.Config as config_module

            reloaded = importlib.reload(config_module)

            with pytest.raises(ValueError) as exc_info:
                reloaded.TuyaConfig.validate()

            assert "API_ENDPOINT" in str(exc_info.value)

    def test_validate_missing_device_id(self, monkeypatch):
        """Test that validation fails when DEVICE_ID is missing."""
        # Mock os.getenv to return None for DEVICE_ID but return values for others
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key == "DEVICE_ID":
                return None
            elif key == "TUYA_ACCESS_ID":
                return "test_id"
            elif key == "TUYA_ACCESS_SECRET":
                return "test_secret"
            elif key == "TUYA_ENDPOINT":
                return "https://test.com"
            return original_getenv(key, default)

        with patch("os.getenv", side_effect=mock_getenv):
            import importlib
            import config.Config as config_module

            reloaded = importlib.reload(config_module)

            with pytest.raises(ValueError) as exc_info:
                reloaded.TuyaConfig.validate()

            assert "DEVICE_ID" in str(exc_info.value)

    def test_validate_multiple_missing_fields(self, monkeypatch):
        """Test that validation reports all missing fields."""
        # Mock os.getenv to return None for TUYA_ACCESS_ID and DEVICE_ID but return values for others
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key == "TUYA_ACCESS_ID":
                return None
            elif key == "DEVICE_ID":
                return None
            elif key == "TUYA_ACCESS_SECRET":
                return "test_secret"
            elif key == "TUYA_ENDPOINT":
                return "https://test.com"
            return original_getenv(key, default)

        with patch("os.getenv", side_effect=mock_getenv):
            import importlib
            import config.Config as config_module

            reloaded = importlib.reload(config_module)

            with pytest.raises(ValueError) as exc_info:
                reloaded.TuyaConfig.validate()

            error_msg = str(exc_info.value)
            assert "ACCESS_ID" in error_msg
            assert "DEVICE_ID" in error_msg


class TestWhatsAppConfig:
    """Test cases for WhatsAppConfig class."""

    def test_api_url_loaded(self, mock_env_vars):
        """Test that WhatsApp API URL is loaded from environment."""
        from config.Config import WhatsAppConfig

        assert WhatsAppConfig.API_URL == "https://api.whatsapp.test/send"

    def test_api_user_loaded(self, mock_env_vars):
        """Test that WhatsApp API user is loaded from environment."""
        from config.Config import WhatsAppConfig

        assert WhatsAppConfig.API_USER == "test_user"

    def test_api_password_loaded(self, mock_env_vars):
        """Test that WhatsApp API password is loaded from environment."""
        from config.Config import WhatsAppConfig

        assert WhatsAppConfig.API_PASSWORD == "test_password"

    def test_group_id_loaded(self, mock_env_vars):
        """Test that WhatsApp group ID is loaded from environment."""
        from config.Config import WhatsAppConfig

        assert WhatsAppConfig.GROUP_ID == "test_group_id"

    def test_validate_success(self, mock_env_vars):
        """Test that validation passes with all required fields."""
        from config.Config import WhatsAppConfig

        # Should not raise any exception
        WhatsAppConfig.validate()

    def test_validate_missing_api_url(self, monkeypatch):
        """Test that validation fails when API_URL is missing."""
        # Mock os.getenv to return None for WA_API_URL but return values for others
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key == "WA_API_URL":
                return None
            elif key == "WA_API_USER":
                return "test_user"
            elif key == "WA_API_PASSWORD":
                return "test_pass"
            elif key == "WA_GROUP_ID":
                return "test_group"
            return original_getenv(key, default)

        with patch("os.getenv", side_effect=mock_getenv):
            import importlib
            import config.Config as config_module

            reloaded = importlib.reload(config_module)

            with pytest.raises(ValueError) as exc_info:
                reloaded.WhatsAppConfig.validate()

            assert "API_URL" in str(exc_info.value)

    def test_validate_missing_api_user(self, monkeypatch):
        """Test that validation fails when API_USER is missing."""
        # Mock os.getenv to return None for WA_API_USER but return values for others
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key == "WA_API_USER":
                return None
            elif key == "WA_API_URL":
                return "https://test.com"
            elif key == "WA_API_PASSWORD":
                return "test_pass"
            elif key == "WA_GROUP_ID":
                return "test_group"
            return original_getenv(key, default)

        with patch("os.getenv", side_effect=mock_getenv):
            import importlib
            import config.Config as config_module

            reloaded = importlib.reload(config_module)

            with pytest.raises(ValueError) as exc_info:
                reloaded.WhatsAppConfig.validate()

            assert "API_USER" in str(exc_info.value)

    def test_validate_missing_api_password(self, monkeypatch):
        """Test that validation fails when API_PASSWORD is missing."""
        # Mock os.getenv to return None for WA_API_PASSWORD but return values for others
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key == "WA_API_PASSWORD":
                return None
            elif key == "WA_API_URL":
                return "https://test.com"
            elif key == "WA_API_USER":
                return "test_user"
            elif key == "WA_GROUP_ID":
                return "test_group"
            return original_getenv(key, default)

        with patch("os.getenv", side_effect=mock_getenv):
            import importlib
            import config.Config as config_module

            reloaded = importlib.reload(config_module)

            with pytest.raises(ValueError) as exc_info:
                reloaded.WhatsAppConfig.validate()

            assert "API_PASSWORD" in str(exc_info.value)

    def test_validate_missing_group_id(self, monkeypatch):
        """Test that validation fails when GROUP_ID is missing."""
        # Mock os.getenv to return None for WA_GROUP_ID but return values for others
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key == "WA_GROUP_ID":
                return None
            elif key == "WA_API_URL":
                return "https://test.com"
            elif key == "WA_API_USER":
                return "test_user"
            elif key == "WA_API_PASSWORD":
                return "test_pass"
            return original_getenv(key, default)

        with patch("os.getenv", side_effect=mock_getenv):
            import importlib
            import config.Config as config_module

            reloaded = importlib.reload(config_module)

            with pytest.raises(ValueError) as exc_info:
                reloaded.WhatsAppConfig.validate()

            assert "GROUP_ID" in str(exc_info.value)

    def test_validate_multiple_missing_fields(self, monkeypatch):
        """Test that validation reports all missing WhatsApp fields."""
        # Mock os.getenv to return None for WA_API_URL and WA_GROUP_ID but return values for others
        original_getenv = os.getenv

        def mock_getenv(key, default=None):
            if key == "WA_API_URL":
                return None
            elif key == "WA_GROUP_ID":
                return None
            elif key == "WA_API_USER":
                return "test_user"
            elif key == "WA_API_PASSWORD":
                return "test_pass"
            return original_getenv(key, default)

        with patch("os.getenv", side_effect=mock_getenv):
            import importlib
            import config.Config as config_module

            reloaded = importlib.reload(config_module)

            with pytest.raises(ValueError) as exc_info:
                reloaded.WhatsAppConfig.validate()

            error_msg = str(exc_info.value)
            assert "API_URL" in error_msg
            assert "GROUP_ID" in error_msg
