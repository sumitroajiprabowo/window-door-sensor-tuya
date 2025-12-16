"""
MQTT Service - Event-Driven Door Sensor Monitoring

This module implements MQTT-based real-time event monitoring for Tuya devices.
Unlike HTTP polling, MQTT uses a publish/subscribe model where the device
pushes status changes to the application instantly.

Benefits:
- Zero delay notifications (instant events)
- Minimal API calls (only when device status changes)
- Efficient for infrequent events (perfect for doors)
- Lower bandwidth usage

Requirements:
- Tuya IoT Platform "Message Subscription" service (paid plan)
- MQTT credentials from Tuya console
"""

import json
import logging
from tuya_connector import TuyaOpenMQ
from config.Config import TuyaConfig
from services.whatsapp_service import (
    send_door_opened_alert,
    send_door_closed_alert,
    send_sensor_initialized_alert,
)

logger = logging.getLogger(__name__)


class DoorSensorMQTT:
    """
    MQTT-based event-driven monitoring for door sensor.

    This class establishes an MQTT connection to Tuya's message broker
    and subscribes to device status change events. When the door opens
    or closes, Tuya pushes an event to this subscriber instantly.

    Perfect for use cases with infrequent events (e.g., door opened 1x/week)
    as it only consumes API quota when actual events occur.
    """

    def __init__(self):
        """
        Initialize MQTT connection to Tuya platform.

        Sets up message handlers for processing incoming device events.
        """
        self.device_id = TuyaConfig.DEVICE_ID
        self.last_door_state = None

        print("\n" + "=" * 60)
        print("Initializing MQTT Event-Driven Monitoring")
        print(f"Device ID: {self.device_id}")
        print("=" * 60)

        # Initialize Tuya MQTT client
        self.mqtt_client = TuyaOpenMQ(
            access_id=TuyaConfig.ACCESS_ID,
            access_secret=TuyaConfig.ACCESS_SECRET,
            endpoint=TuyaConfig.API_ENDPOINT,
        )

        # Register message handler
        self.mqtt_client.add_message_listener(self._on_message)

        logger.info("MQTT client initialized")

    def _on_message(self, msg):
        """
        Handle incoming MQTT messages from Tuya platform.

        This callback is triggered when the device publishes a status change.
        Processes the message and triggers appropriate WhatsApp alerts.

        Args:
            msg: MQTT message containing device status update

        Message format:
        {
            "dataId": "device_id",
            "devId": "device_id",
            "productKey": "product_key",
            "status": [
                {
                    "code": "doorcontact_state",
                    "value": true/false,
                    "t": timestamp
                },
                {
                    "code": "battery_percentage",
                    "value": 100,
                    "t": timestamp
                }
            ]
        }
        """
        try:
            print("\n" + "=" * 60)
            print("[MQTT EVENT RECEIVED]")
            print("=" * 60)

            # Parse message payload
            data = json.loads(msg.payload.decode("utf-8"))
            logger.info(f"MQTT message received: {data}")

            # Extract device ID and status
            device_id = data.get("devId")
            status_list = data.get("status", [])

            # Filter for our device
            if device_id != self.device_id:
                logger.debug(f"Ignoring message for different device: {device_id}")
                return

            # Extract door state and battery from status
            door_state = None
            battery = None

            for status in status_list:
                code = status.get("code")
                value = status.get("value")

                if code == "doorcontact_state":
                    door_state = value
                elif code == "battery_percentage":
                    battery = value

            # Process door state change
            if door_state is not None:
                timestamp = data.get("t", 0)

                # Handle initial state (first message)
                if self.last_door_state is None:
                    state_text = "OPENED" if door_state else "CLOSED"

                    print(f"[SENSOR INITIALIZED] First event")
                    print(f"   Current state: Door {state_text}")
                    print(f"   Timestamp: {timestamp}")
                    print(f"   Device ID: {device_id}")
                    if battery:
                        print(f"   Battery: {battery}%")
                    print("=" * 60)

                    # Send initialization message
                    send_sensor_initialized_alert()
                    self.last_door_state = door_state
                    return

                # Detect state change
                if door_state != self.last_door_state:
                    print(
                        f"[DOOR STATE CHANGE] Door was {'opened' if self.last_door_state else 'closed'}, "
                        f"now {'opened' if door_state else 'closed'}"
                    )

                    if door_state:
                        # Door opened
                        print(f"🚪 DOOR OPENED (doorcontact_state = True)")
                        print(f"   Timestamp: {timestamp}")
                        print(f"   Device ID: {device_id}")
                        if battery:
                            print(f"   Battery: {battery}%")
                        print("=" * 60)

                        send_door_opened_alert()
                    else:
                        # Door closed
                        print(f"🚪 DOOR CLOSED (doorcontact_state = False)")
                        print(f"   Timestamp: {timestamp}")
                        print(f"   Device ID: {device_id}")
                        if battery:
                            print(f"   Battery: {battery}%")
                        print("=" * 60)

                        send_door_closed_alert()

                    # Update state tracker
                    self.last_door_state = door_state

        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}", exc_info=True)
            print(f"❌ Error processing MQTT message: {e}")

    def start(self):
        """
        Start MQTT listener and begin monitoring for events.

        Establishes connection to Tuya MQTT broker and subscribes to
        device status change topic. Blocks until connection is lost.
        """
        print("\n" + "=" * 60)
        print("Starting MQTT Event-Driven Monitoring")
        print("Waiting for door sensor events...")
        print("=" * 60)

        try:
            # Start MQTT client (blocking call)
            self.mqtt_client.start()
            logger.info("MQTT monitoring started successfully")

            print("✅ MQTT monitoring started successfully!")
            print("Listening for real-time door events...")
            print("=" * 60 + "\n")

        except Exception as e:
            logger.error(f"Failed to start MQTT client: {e}", exc_info=True)
            print(f"\n❌ Failed to start MQTT monitoring: {e}")
            print("=" * 60)
            raise

    def stop(self):
        """
        Stop MQTT listener gracefully.

        Disconnects from Tuya MQTT broker and cleans up resources.
        """
        try:
            self.mqtt_client.stop()
            logger.info("MQTT monitoring stopped")
            print("MQTT monitoring stopped")
        except Exception as e:
            logger.error(f"Error stopping MQTT client: {e}")


# Global singleton instance
door_mqtt = DoorSensorMQTT()
