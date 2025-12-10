"""
Unit tests for services/polling_service.py module.

Tests HTTP polling service for door sensor monitoring.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock, call
import sys
from io import StringIO


class TestDoorSensorPollerInit:
    """Test cases for DoorSensorPoller initialization."""

    @patch("services.polling_service.TuyaConfig")
    @patch("services.polling_service.Config")
    def test_poller_init_default_poll_interval(self, mock_config, mock_tuya_config, mock_env_vars):
        """Test that default poll interval is used from Config."""
        mock_config.POLL_INTERVAL = 5

        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller()

        assert poller.poll_interval == 5

    @patch("services.polling_service.TuyaConfig")
    def test_poller_init_custom_poll_interval(self, mock_tuya_config, mock_env_vars):
        """Test that custom poll interval can be specified."""
        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller(poll_interval=10)

        assert poller.poll_interval == 10

    @patch("services.polling_service.TuyaConfig")
    def test_poller_init_device_id(self, mock_tuya_config, mock_env_vars):
        """Test that device ID is loaded from TuyaConfig."""
        mock_tuya_config.DEVICE_ID = "test_device_123"

        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller()

        assert poller.device_id == "test_device_123"

    @patch("services.polling_service.TuyaConfig")
    def test_poller_init_running_false(self, mock_tuya_config, mock_env_vars):
        """Test that running flag is initially False."""
        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller()

        assert poller.running is False

    @patch("services.polling_service.TuyaConfig")
    def test_poller_init_thread_none(self, mock_tuya_config, mock_env_vars):
        """Test that thread is initially None."""
        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller()

        assert poller.thread is None

    @patch("services.polling_service.TuyaConfig")
    def test_poller_init_last_door_state_none(self, mock_tuya_config, mock_env_vars):
        """Test that last_door_state is initially None."""
        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller()

        assert poller.last_door_state is None


class TestDoorSensorPollerPollLoop:
    """Test cases for DoorSensorPoller._poll_loop method."""

    @patch("services.polling_service.tuya_service")
    @patch("services.polling_service.time.sleep")
    @patch("services.polling_service.TuyaConfig")
    def test_poll_loop_queries_tuya_service(
        self, mock_tuya_config, mock_sleep, mock_tuya_service, mock_env_vars
    ):
        """Test that poll loop queries tuya_service for device status."""
        mock_tuya_config.DEVICE_ID = "test_device"
        mock_tuya_service.get_device_status.return_value = {
            "success": True,
            "result": [{"code": "doorcontact_state", "value": False}],
        }

        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller(poll_interval=1)
        poller.running = True

        # Run one iteration then stop
        def stop_after_one(*args):
            poller.running = False

        mock_sleep.side_effect = stop_after_one

        poller._poll_loop()

        mock_tuya_service.get_device_status.assert_called_with("test_device")

    @patch("services.polling_service.tuya_service")
    @patch("services.polling_service.time.sleep")
    @patch("services.polling_service.TuyaConfig")
    def test_poll_loop_sleeps_between_polls(
        self, mock_tuya_config, mock_sleep, mock_tuya_service, mock_env_vars
    ):
        """Test that poll loop sleeps for poll_interval between iterations."""
        mock_tuya_service.get_device_status.return_value = {"success": True, "result": []}

        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller(poll_interval=3)
        poller.running = True

        def stop_after_one(*args):
            poller.running = False

        mock_sleep.side_effect = stop_after_one

        poller._poll_loop()

        mock_sleep.assert_called_with(3)

    @patch("services.polling_service.tuya_service")
    @patch("services.polling_service.send_door_opened_alert")
    @patch("services.polling_service.time.sleep")
    @patch("services.polling_service.TuyaConfig")
    def test_poll_loop_detects_door_opened(
        self, mock_tuya_config, mock_sleep, mock_alert, mock_tuya_service, mock_env_vars
    ):
        """Test that poll loop detects door opened event."""
        mock_tuya_service.get_device_status.return_value = {
            "success": True,
            "result": [{"code": "doorcontact_state", "value": True}],
        }

        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller(poll_interval=1)
        poller.running = True
        poller.last_door_state = False  # Door was closed

        def stop_after_one(*args):
            poller.running = False

        mock_sleep.side_effect = stop_after_one

        poller._poll_loop()

        mock_alert.assert_called_once()

    @patch("services.polling_service.tuya_service")
    @patch("services.polling_service.send_door_closed_alert")
    @patch("services.polling_service.time.sleep")
    @patch("services.polling_service.TuyaConfig")
    def test_poll_loop_detects_door_closed(
        self, mock_tuya_config, mock_sleep, mock_alert, mock_tuya_service, mock_env_vars
    ):
        """Test that poll loop detects door closed event."""
        mock_tuya_service.get_device_status.return_value = {
            "success": True,
            "result": [{"code": "doorcontact_state", "value": False}],
        }

        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller(poll_interval=1)
        poller.running = True
        poller.last_door_state = True  # Door was open

        def stop_after_one(*args):
            poller.running = False

        mock_sleep.side_effect = stop_after_one

        poller._poll_loop()

        mock_alert.assert_called_once()

    @patch("services.polling_service.tuya_service")
    @patch("services.polling_service.send_door_opened_alert")
    @patch("services.polling_service.time.sleep")
    @patch("services.polling_service.TuyaConfig")
    def test_poll_loop_no_alert_on_same_state(
        self, mock_tuya_config, mock_sleep, mock_alert, mock_tuya_service, mock_env_vars
    ):
        """Test that no alert is sent when state doesn't change."""
        mock_tuya_service.get_device_status.return_value = {
            "success": True,
            "result": [{"code": "doorcontact_state", "value": True}],
        }

        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller(poll_interval=1)
        poller.running = True
        poller.last_door_state = True  # Door was already open

        def stop_after_one(*args):
            poller.running = False

        mock_sleep.side_effect = stop_after_one

        poller._poll_loop()

        mock_alert.assert_not_called()

    @patch("services.polling_service.tuya_service")
    @patch("services.polling_service.time.sleep")
    @patch("services.polling_service.TuyaConfig")
    def test_poll_loop_sets_initial_state(
        self, mock_tuya_config, mock_sleep, mock_tuya_service, mock_env_vars
    ):
        """Test that poll loop sets initial state when last_door_state is None."""
        mock_tuya_service.get_device_status.return_value = {
            "success": True,
            "result": [{"code": "doorcontact_state", "value": False}],
        }

        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller(poll_interval=1)
        poller.running = True
        poller.last_door_state = None

        def stop_after_one(*args):
            poller.running = False

        mock_sleep.side_effect = stop_after_one

        poller._poll_loop()

        assert poller.last_door_state is False

    @patch("services.polling_service.tuya_service")
    @patch("services.polling_service.time.sleep")
    @patch("services.polling_service.TuyaConfig")
    def test_poll_loop_extracts_battery_percentage(
        self, mock_tuya_config, mock_sleep, mock_tuya_service, mock_env_vars
    ):
        """Test that poll loop extracts battery percentage from status."""
        mock_tuya_service.get_device_status.return_value = {
            "success": True,
            "result": [
                {"code": "doorcontact_state", "value": False},
                {"code": "battery_percentage", "value": 85},
            ],
        }

        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller(poll_interval=1)
        poller.running = True

        def stop_after_one(*args):
            poller.running = False

        mock_sleep.side_effect = stop_after_one

        # Should not raise any exception
        poller._poll_loop()

    @patch("services.polling_service.tuya_service")
    @patch("services.polling_service.time.sleep")
    @patch("services.polling_service.logging")
    @patch("services.polling_service.TuyaConfig")
    def test_poll_loop_handles_api_failure(
        self, mock_tuya_config, mock_logging, mock_sleep, mock_tuya_service, mock_env_vars
    ):
        """Test that poll loop handles API failure gracefully."""
        mock_tuya_service.get_device_status.return_value = {"success": False, "msg": "API error"}

        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller(poll_interval=1)
        poller.running = True

        def stop_after_one(*args):
            poller.running = False

        mock_sleep.side_effect = stop_after_one

        # Should not raise exception
        poller._poll_loop()

        mock_logging.warning.assert_called()

    @patch("services.polling_service.tuya_service")
    @patch("services.polling_service.time.sleep")
    @patch("services.polling_service.logging")
    @patch("services.polling_service.TuyaConfig")
    def test_poll_loop_handles_exception(
        self, mock_tuya_config, mock_logging, mock_sleep, mock_tuya_service, mock_env_vars
    ):
        """Test that poll loop handles exceptions gracefully."""
        mock_tuya_service.get_device_status.side_effect = Exception("Network error")

        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller(poll_interval=1)
        poller.running = True

        def stop_after_one(*args):
            poller.running = False

        mock_sleep.side_effect = stop_after_one

        # Should not raise exception
        poller._poll_loop()

        mock_logging.error.assert_called()


class TestDoorSensorPollerStart:
    """Test cases for DoorSensorPoller.start method."""

    @patch("services.polling_service.threading.Thread")
    @patch("services.polling_service.TuyaConfig")
    def test_start_creates_thread(self, mock_tuya_config, mock_thread, mock_env_vars):
        """Test that start creates a daemon thread."""
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller()
        poller.start()

        mock_thread.assert_called_once()
        assert mock_thread.call_args[1]["daemon"] is True

    @patch("services.polling_service.threading.Thread")
    @patch("services.polling_service.TuyaConfig")
    def test_start_sets_running_flag(self, mock_tuya_config, mock_thread, mock_env_vars):
        """Test that start sets running flag to True."""
        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller()
        poller.start()

        assert poller.running is True

    @patch("services.polling_service.threading.Thread")
    @patch("services.polling_service.TuyaConfig")
    def test_start_starts_thread(self, mock_tuya_config, mock_thread, mock_env_vars):
        """Test that start calls thread.start()."""
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller()
        poller.start()

        mock_thread_instance.start.assert_called_once()

    @patch("services.polling_service.threading.Thread")
    @patch("services.polling_service.logging")
    @patch("services.polling_service.TuyaConfig")
    def test_start_prevents_duplicate_start(
        self, mock_tuya_config, mock_logging, mock_thread, mock_env_vars
    ):
        """Test that start does nothing if already running."""
        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller()
        poller.running = True

        poller.start()

        mock_thread.assert_not_called()
        mock_logging.warning.assert_called_with("Polling already running")


class TestDoorSensorPollerStop:
    """Test cases for DoorSensorPoller.stop method."""

    @patch("services.polling_service.TuyaConfig")
    def test_stop_sets_running_flag_false(self, mock_tuya_config, mock_env_vars):
        """Test that stop sets running flag to False."""
        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller()
        poller.running = True
        poller.stop()

        assert poller.running is False

    @patch("services.polling_service.TuyaConfig")
    def test_stop_joins_thread(self, mock_tuya_config, mock_env_vars):
        """Test that stop joins the thread with timeout."""
        from services.polling_service import DoorSensorPoller

        mock_thread = Mock()
        poller = DoorSensorPoller()
        poller.thread = mock_thread
        poller.stop()

        mock_thread.join.assert_called_once_with(timeout=5)

    @patch("services.polling_service.TuyaConfig")
    def test_stop_handles_no_thread(self, mock_tuya_config, mock_env_vars):
        """Test that stop handles case when thread is None."""
        from services.polling_service import DoorSensorPoller

        poller = DoorSensorPoller()
        poller.thread = None

        # Should not raise exception
        poller.stop()


class TestDoorSensorPollerSingleton:
    """Test cases for door_poller singleton instance."""

    @patch("services.polling_service.TuyaConfig")
    def test_door_poller_singleton_exists(self, mock_tuya_config, mock_env_vars):
        """Test that door_poller singleton instance is created."""
        from services import polling_service

        assert hasattr(polling_service, "door_poller")
        assert polling_service.door_poller is not None

    @patch("services.polling_service.TuyaConfig")
    def test_door_poller_singleton_is_door_sensor_poller_instance(
        self, mock_tuya_config, mock_env_vars
    ):
        """Test that door_poller is an instance of DoorSensorPoller."""
        from services.polling_service import door_poller, DoorSensorPoller

        assert isinstance(door_poller, DoorSensorPoller)
