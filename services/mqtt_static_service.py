"""
MQTT Static Service - Alternative MQTT Implementation

This module provides MQTT monitoring using static credentials instead of
dynamic OpenHub API credentials. Use this if:
1. OpenHub API not available (free tier limitation)
2. Prefer manual credential management
3. Need simpler setup

Requires manual MQTT credential setup from Tuya console.
"""

import json
import logging
import time
import ssl
from typing import Optional
import paho.mqtt.client as mqtt
from config.Config import TuyaConfig
from services.whatsapp_service import (
    send_door_opened_alert,
    send_door_closed_alert,
    send_sensor_initialized_alert,
)

logger = logging.getLogger(__name__)


class TuyaMQTTStatic:
    """
    Static MQTT client for Tuya device monitoring.

    Uses pre-configured MQTT credentials instead of dynamic API generation.
    Simpler but requires manual credential setup.
    """

    def __init__(
        self,
        mqtt_host: str = "m1-sg.iotbing.com",
        mqtt_port: int = 8883,
        client_id: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        Initialize static MQTT client.

        Args:
            mqtt_host: MQTT broker hostname (default: Singapore DC)
            mqtt_port: MQTT broker port (default: 8883 for SSL)
            client_id: MQTT client ID (if None, uses access_id)
            username: MQTT username (if None, uses access_id)
            password: MQTT password (if None, uses access_secret)
        """
        self.device_id = TuyaConfig.DEVICE_ID
        self.last_door_state = None

        # MQTT connection parameters
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.client_id = client_id or TuyaConfig.ACCESS_ID
        self.username = username or TuyaConfig.ACCESS_ID
        self.password = password or TuyaConfig.ACCESS_SECRET

        # Construct topic for this device
        # Format: tylink/{access_id}/device/status/{device_id}
        self.topic = f"tylink/{TuyaConfig.ACCESS_ID}/device/status/{self.device_id}"

        self.mqtt_client: Optional[mqtt.Client] = None

        logger.info("TuyaMQTTStatic initialized")

    def _on_connect(self, client, userdata, flags, rc):
        """Callback when MQTT connection is established."""
        if rc == 0:
            print("\n" + "=" * 60)
            print("✅ MQTT Connection Established (Static Credentials)")
            print("=" * 60)
            logger.info("MQTT connected successfully")

            # Subscribe to device status topic
            client.subscribe(self.topic)
            print(f"📡 Subscribed to topic: {self.topic}")
            print("   Waiting for device events...")
            print("=" * 60 + "\n")
            logger.info(f"Subscribed to topic: {self.topic}")
        else:
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorized",
            }
            error_msg = error_messages.get(rc, f"Unknown error ({rc})")
            print(f"\n❌ MQTT Connection Failed: {error_msg}")
            logger.error(f"MQTT connection failed: {error_msg}")

    def _on_disconnect(self, client, userdata, rc):
        """Callback when MQTT connection is lost."""
        if rc != 0:
            print(f"\n⚠️  MQTT Connection Lost (code: {rc})")
            print("   Will attempt to reconnect...")
            logger.warning(f"MQTT disconnected unexpectedly (rc={rc})")
        else:
            print("\n✅ MQTT Disconnected Cleanly")
            logger.info("MQTT disconnected")

    def _on_message(self, client, userdata, msg):
        """Callback when MQTT message is received."""
        try:
            print("\n" + "=" * 60)
            print("[MQTT EVENT RECEIVED]")
            print("=" * 60)

            # Parse message payload
            payload = json.loads(msg.payload.decode("utf-8"))
            logger.info(f"MQTT message received on {msg.topic}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

            # Extract status data
            # Tuya MQTT message format varies, try multiple patterns
            status_list = []

            # Pattern 1: Direct status field
            if "status" in payload:
                status_list = payload.get("status", [])

            # Pattern 2: Data wrapper
            elif "data" in payload:
                data = payload.get("data", {})
                if isinstance(data, str):
                    data = json.loads(data)
                status_list = data.get("status", [])

            # Extract door state and battery
            door_state = None
            battery = None

            for status in status_list:
                code = status.get("code")
                value = status.get("value")

                if code == "doorcontact_state":
                    door_state = value
                    print(f"   doorcontact_state: {value}")
                elif code == "battery_percentage":
                    battery = value
                    print(f"   battery_percentage: {value}%")

            # Process door state change
            if door_state is not None:
                timestamp = int(time.time() * 1000)

                # Handle initial state (first message)
                if self.last_door_state is None:
                    state_text = "OPENED" if door_state else "CLOSED"

                    print(f"\n[SENSOR INITIALIZED] First event")
                    print(f"   Current state: Door {state_text}")
                    print(f"   Timestamp: {timestamp}")
                    print(f"   Device ID: {self.device_id}")
                    if battery:
                        print(f"   Battery: {battery}%")
                    print("=" * 60)

                    send_sensor_initialized_alert()
                    self.last_door_state = door_state
                    return

                # Detect state change
                if door_state != self.last_door_state:
                    print(
                        f"\n[DOOR STATE CHANGE] Door was {'opened' if self.last_door_state else 'closed'}, "
                        f"now {'opened' if door_state else 'closed'}"
                    )

                    if door_state:
                        # Door opened
                        print(f"🚪 DOOR OPENED (doorcontact_state = True)")
                        print(f"   Timestamp: {timestamp}")
                        print(f"   Device ID: {self.device_id}")
                        if battery:
                            print(f"   Battery: {battery}%")
                        print("=" * 60)

                        send_door_opened_alert()
                    else:
                        # Door closed
                        print(f"🚪 DOOR CLOSED (doorcontact_state = False)")
                        print(f"   Timestamp: {timestamp}")
                        print(f"   Device ID: {self.device_id}")
                        if battery:
                            print(f"   Battery: {battery}%")
                        print("=" * 60)

                        send_door_closed_alert()

                    # Update state tracker
                    self.last_door_state = door_state

        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}", exc_info=True)
            print(f"❌ Error processing message: {e}")

    def connect(self):
        """Connect to Tuya MQTT broker with static credentials."""
        print("\n" + "=" * 60)
        print("MQTT Static Connection Setup")
        print("=" * 60)
        print(f"   Host: {self.mqtt_host}")
        print(f"   Port: {self.mqtt_port}")
        print(f"   Client ID: {self.client_id}")
        print(f"   Topic: {self.topic}")
        print("=" * 60)

        # Create MQTT client
        self.mqtt_client = mqtt.Client(client_id=self.client_id)

        # Set authentication
        self.mqtt_client.username_pw_set(self.username, self.password)

        # Configure SSL/TLS
        self.mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
        self.mqtt_client.tls_insecure_set(True)

        # Set callbacks
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        self.mqtt_client.on_message = self._on_message

        # Connect to broker
        logger.info(f"Connecting to MQTT broker: {self.mqtt_host}:{self.mqtt_port}")
        print(f"\n📡 Connecting to {self.mqtt_host}:{self.mqtt_port}...")

        self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, keepalive=60)

    def start(self):
        """Start MQTT monitoring loop."""
        print("\n" + "=" * 60)
        print("Starting MQTT Static Monitoring")
        print(f"Device ID: {self.device_id}")
        print("=" * 60)

        try:
            # Connect to MQTT broker
            self.connect()

            # Start MQTT loop (blocking)
            print("\n🎧 Listening for door sensor events...")
            print("Press Ctrl+C to stop\n")

            self.mqtt_client.loop_forever()

        except KeyboardInterrupt:
            print("\n\n⏹️  Stopping MQTT monitoring...")
            self.stop()
        except Exception as e:
            logger.error(f"Error in MQTT monitoring: {e}", exc_info=True)
            print(f"\n❌ MQTT monitoring error: {e}")
            raise

    def stop(self):
        """Stop MQTT connection gracefully."""
        if self.mqtt_client:
            self.mqtt_client.disconnect()
            self.mqtt_client.loop_stop()
            logger.info("MQTT monitoring stopped")
            print("✅ MQTT monitoring stopped")


# Global singleton instance (Singapore DC)
mqtt_static = TuyaMQTTStatic(
    mqtt_host="m1-sg.iotbing.com",
    mqtt_port=8883,
)
