"""
Polling Service - HTTP-based Door Sensor Monitoring

This module implements periodic polling of the Tuya HTTP API to monitor
door sensor status. It serves as an alternative to the Pulsar WebSocket
listener, providing more reliable connectivity in environments with
encryption or network restrictions.
"""

import time
import logging
import threading
import sys
from services.tuya_service import tuya_service
from services.whatsapp_service import (
    send_door_opened_alert,
    send_door_closed_alert,
    send_sensor_initialized_alert,
)
from config.Config import TuyaConfig, Config


class DoorSensorPoller:
    """
    HTTP-based polling service for door sensor monitoring.

    This class periodically queries the Tuya Cloud API to check the door
    sensor status and detects state changes. It runs in a background thread
    and sends WhatsApp alerts when the door opens or closes.

    This polling approach is more reliable than WebSocket in certain network
    environments and doesn't require complex encryption handling.
    """

    def __init__(self, poll_interval=None):
        """
        Initialize the door sensor poller.

        Args:
            poll_interval (int, optional): Seconds between status checks.
                Defaults to Config.POLL_INTERVAL if not specified.
        """
        self.device_id = TuyaConfig.DEVICE_ID
        self.poll_interval = poll_interval or Config.POLL_INTERVAL
        self.running = False
        self.thread = None
        self.last_door_state = None  # Tracks previous state to detect changes

    def _poll_loop(self):
        """
        Main polling loop that runs in a background thread.

        Continuously queries the Tuya API at regular intervals to check
        door sensor status. Detects state changes and triggers alerts.
        """
        print(f"\nPolling started - checking every {self.poll_interval} seconds")
        print("=" * 60)
        sys.stdout.flush()

        while self.running:
            try:
                # Query device status from Tuya Cloud API
                response = tuya_service.get_device_status(self.device_id)

                if response.get("success"):
                    result = response.get("result", [])

                    # Extract door contact state and battery level from status
                    door_state = None
                    battery = None

                    for status in result:
                        if status.get("code") == "doorcontact_state":
                            door_state = status.get("value")
                        elif status.get("code") == "battery_percentage":
                            battery = status.get("value")

                    # Handle initial state detection (first reading after service start)
                    if self.last_door_state is None and door_state is not None:
                        timestamp = int(time.time() * 1000)
                        state_text = "OPENED" if door_state else "CLOSED"

                        print(f"\n[SENSOR INITIALIZED] First reading")
                        print(f"   Current state: Door {state_text}")
                        print(f"   Timestamp: {timestamp}")
                        print(f"   Device ID: {self.device_id}")
                        if battery:
                            print(f"   Battery: {battery}%")
                        sys.stdout.flush()

                        # Send initialization message instead of door state alert
                        send_sensor_initialized_alert()

                        # Update state tracker
                        self.last_door_state = door_state

                    # Detect actual state changes (not initial state)
                    elif door_state is not None and door_state != self.last_door_state:
                        timestamp = int(time.time() * 1000)

                        print(
                            f"\n[DOOR STATE CHANGE] Door was {'opened' if self.last_door_state else 'closed'}, now {'opened' if door_state else 'closed'}"
                        )

                        if door_state:
                            # Door opened event
                            print(f"DOOR OPENED (doorcontact_state = True)")
                            print(f"   Timestamp: {timestamp}")
                            print(f"   Device ID: {self.device_id}")
                            if battery:
                                print(f"   Battery: {battery}%")
                            sys.stdout.flush()

                            # Trigger WhatsApp alert for door opened
                            send_door_opened_alert()
                        else:
                            # Door closed event
                            print(f"DOOR CLOSED (doorcontact_state = False)")
                            print(f"   Timestamp: {timestamp}")
                            print(f"   Device ID: {self.device_id}")
                            if battery:
                                print(f"   Battery: {battery}%")
                            sys.stdout.flush()

                            # Trigger WhatsApp alert for door closed
                            send_door_closed_alert()

                        # Update state tracker
                        self.last_door_state = door_state

                else:
                    error_msg = response.get("msg", "Unknown error")
                    error_code = response.get("code", "")

                    # Check for quota exhaustion or permission errors
                    if (
                        "quota" in error_msg.lower()
                        or "permission" in error_msg.lower()
                        or error_code == 1106
                    ):
                        # Use exponential backoff for quota errors
                        logging.error(f"⚠️  QUOTA EXHAUSTED: {error_msg}")
                        logging.error(f"⏸️  Pausing polling for 1 hour to preserve quota...")

                        # Sleep for 1 hour instead of stopping completely
                        time.sleep(3600)  # 3600 seconds = 1 hour

                        logging.info("♻️  Resuming polling after 1 hour pause...")
                        continue
                    else:
                        # Other errors - log but continue with normal interval
                        logging.warning(f"Failed to get device status: {error_msg}")

            except Exception as e:
                logging.error(f"Error in polling loop: {e}")

            # Wait before next poll to avoid overwhelming the API
            time.sleep(self.poll_interval)

    def start(self):
        """
        Start the polling service in a background thread.

        Creates and starts a daemon thread that continuously polls the
        Tuya API. Prevents duplicate starts if already running.
        """
        if self.running:
            logging.warning("Polling already running")
            return

        print("\n" + "=" * 60)
        print("Starting HTTP Polling Service (Pulsar Alternative)")
        print(f"API Endpoint: {TuyaConfig.API_ENDPOINT}")
        print(f"Device ID: {self.device_id}")
        print(f"Poll Interval: {self.poll_interval} seconds")
        print("=" * 60)
        print("Monitoring door sensor via HTTP API polling...")
        print("Legend: Door Opened | Door Closed")
        print("=" * 60)

        self.running = True
        # Create daemon thread so it terminates when main program exits
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

        print("HTTP Polling started successfully!")
        print("=" * 60 + "\n")

    def stop(self):
        """
        Stop the polling service gracefully.

        Sets the running flag to False and waits for the polling thread
        to terminate within a timeout period.
        """
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("HTTP Polling stopped")


# Global singleton instance for application-wide use
door_poller = DoorSensorPoller()
