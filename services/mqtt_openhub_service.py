"""
MQTT OpenHub Service - Dynamic MQTT Connection for Tuya Devices

This module implements MQTT event monitoring using Tuya's OpenHub API
for dynamic credential generation. Unlike static credentials, this approach
generates fresh MQTT credentials on-demand with automatic expiration handling.

API Endpoint: POST /v1.0/iot-03/open-hub/access-config

Benefits:
- Dynamic credential generation (auto-refresh)
- Standard MQTT protocol (paho-mqtt)
- Event-driven (zero polling overhead)
- Perfect for infrequent events (e.g., door opened 1x/week)
"""

import json
import logging
import time
import ssl
from typing import Optional, Dict
import paho.mqtt.client as mqtt
from tuya_connector import TuyaOpenAPI
from config.Config import TuyaConfig
from services.whatsapp_service import (
    send_door_opened_alert,
    send_door_closed_alert,
    send_sensor_initialized_alert,
)

logger = logging.getLogger(__name__)


class TuyaMQTTOpenHub:
    """
    MQTT client using Tuya OpenHub dynamic credential API.

    Generates MQTT credentials dynamically, connects to Tuya MQTT broker,
    and subscribes to device events for real-time door sensor monitoring.
    """

    def __init__(self):
        """Initialize MQTT OpenHub client with Tuya API credentials."""
        self.device_id = TuyaConfig.DEVICE_ID
        self.last_door_state = None

        # Initialize Tuya OpenAPI client for credential generation
        self.api = TuyaOpenAPI(
            endpoint=TuyaConfig.API_ENDPOINT,
            access_id=TuyaConfig.ACCESS_ID,
            access_secret=TuyaConfig.ACCESS_SECRET,
        )
        self.api.connect()

        # MQTT connection parameters (will be populated from API)
        self.mqtt_client: Optional[mqtt.Client] = None
        self.mqtt_url: Optional[str] = None
        self.mqtt_port: Optional[int] = None
        self.client_id: Optional[str] = None
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.source_topic: Optional[str] = None
        self.expire_time: Optional[int] = None

        logger.info("TuyaMQTTOpenHub initialized")

    def _get_mqtt_config(self) -> Dict:
        """
        Get MQTT connection configuration from Tuya OpenHub API.

        Calls POST /v1.0/iot-03/open-hub/access-config to generate
        dynamic MQTT credentials and connection parameters.

        Returns:
            Dict containing MQTT configuration:
            - url: MQTT broker URL (ssl://host:port)
            - client_id: MQTT client ID
            - username: Authentication username
            - password: Authentication password
            - expire_time: Credential validity in seconds
            - source_topic: Topic to subscribe for device events

        Raises:
            Exception: If API call fails or returns error
        """
        print("\n" + "=" * 60)
        print("Generating MQTT Connection Configuration")
        print("=" * 60)

        # Prepare API request
        endpoint = "/v1.0/iot-03/open-hub/access-config"
        body = {
            # uid omitted - not required for device-level access
            "link_id": f"door-sensor-{int(time.time())}",  # Unique link ID
            "link_type": "mqtt",  # MQTT connection type
            "topics": "device",  # Subscribe to device events
            "msg_encrypted_version": "2.0",  # Message encryption version (use 2.0)
        }

        logger.info(f"Requesting MQTT config from: {endpoint}")
        logger.debug(f"Request body: {json.dumps(body, indent=2)}")

        # Call Tuya API
        response = self.api.post(endpoint, body)

        if not response.get("success"):
            error_msg = response.get("msg", "Unknown error")
            error_code = response.get("code", "")
            logger.error(f"Failed to get MQTT config: {error_msg} (code: {error_code})")
            raise Exception(f"MQTT config API failed: {error_msg}")

        result = response.get("result", {})

        print(f"✅ MQTT Configuration Retrieved")
        print(f"   Broker URL: {result.get('url')}")
        print(f"   Client ID: {result.get('client_id')}")
        print(f"   Expires in: {result.get('expire_time')} seconds")
        print("=" * 60)

        logger.info("MQTT configuration retrieved successfully")
        logger.debug(f"MQTT config: {json.dumps(result, indent=2)}")

        return result

    def _parse_mqtt_url(self, url: str) -> tuple:
        """
        Parse MQTT URL to extract protocol, host, and port.

        Args:
            url: MQTT URL in format "ssl://host:port" or "tcp://host:port"

        Returns:
            Tuple of (protocol, host, port, use_ssl)
        """
        # Example: ssl://m1.tuyacn.com:8883
        if url.startswith("ssl://"):
            protocol = "ssl"
            use_ssl = True
            url = url.replace("ssl://", "")
        elif url.startswith("tcp://"):
            protocol = "tcp"
            use_ssl = False
            url = url.replace("tcp://", "")
        else:
            # Default to SSL
            protocol = "ssl"
            use_ssl = True

        # Split host:port
        if ":" in url:
            host, port_str = url.rsplit(":", 1)
            port = int(port_str)
        else:
            host = url
            port = 8883 if use_ssl else 1883  # Default MQTT ports

        return protocol, host, port, use_ssl

    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback when MQTT connection is established.

        Args:
            client: MQTT client instance
            userdata: User data (unused)
            flags: Connection flags
            rc: Return code (0 = success)
        """
        if rc == 0:
            print("\n" + "=" * 60)
            print("✅ MQTT Connection Established")
            print("=" * 60)
            logger.info("MQTT connected successfully")

            # Subscribe to device topic
            if self.source_topic:
                client.subscribe(self.source_topic)
                print(f"📡 Subscribed to topic: {self.source_topic}")
                print("   Waiting for device events...")
                print("=" * 60 + "\n")
                logger.info(f"Subscribed to topic: {self.source_topic}")
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
        """
        Callback when MQTT connection is lost.

        Args:
            client: MQTT client instance
            userdata: User data (unused)
            rc: Return code (0 = clean disconnect)
        """
        if rc != 0:
            print(f"\n⚠️  MQTT Connection Lost (code: {rc})")
            print("   Will attempt to reconnect...")
            logger.warning(f"MQTT disconnected unexpectedly (rc={rc})")
        else:
            print("\n✅ MQTT Disconnected Cleanly")
            logger.info("MQTT disconnected")

    def _on_message(self, client, userdata, msg):
        """
        Callback when MQTT message is received.

        Processes device status updates and triggers WhatsApp alerts
        when door opens or closes.

        Args:
            client: MQTT client instance
            userdata: User data (unused)
            msg: MQTT message with device status
        """
        try:
            print("\n" + "=" * 60)
            print("[MQTT EVENT RECEIVED]")
            print("=" * 60)

            # Parse message payload
            payload = json.loads(msg.payload.decode("utf-8"))
            logger.info(f"MQTT message received on {msg.topic}")
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

            # Extract protocol and data
            protocol = payload.get("protocol", 0)
            data_str = payload.get("data", "{}")

            # Parse data field (might be JSON string)
            if isinstance(data_str, str):
                data = json.loads(data_str)
            else:
                data = data_str

            # Extract device ID and status
            device_id = data.get("devId")
            status_list = data.get("status", [])

            # Filter for our device
            if device_id != self.device_id:
                logger.debug(f"Ignoring message for different device: {device_id}")
                return

            print(f"Device: {device_id}")
            print(f"Protocol: {protocol}")

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
                timestamp = data.get("t", int(time.time() * 1000))

                # Handle initial state (first message)
                if self.last_door_state is None:
                    state_text = "OPENED" if door_state else "CLOSED"

                    print(f"\n[SENSOR INITIALIZED] First event")
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
                        f"\n[DOOR STATE CHANGE] Door was {'opened' if self.last_door_state else 'closed'}, "
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
            print(f"❌ Error processing message: {e}")

    def connect(self):
        """
        Connect to Tuya MQTT broker using OpenHub API credentials.

        Steps:
        1. Get MQTT configuration from Tuya API
        2. Parse connection parameters
        3. Create MQTT client
        4. Configure SSL if needed
        5. Connect to broker
        6. Subscribe to device topic
        """
        # Get MQTT configuration from API
        config = self._get_mqtt_config()

        # Parse configuration
        self.mqtt_url = config.get("url")
        self.client_id = config.get("client_id")
        self.username = config.get("username")
        self.password = config.get("password")
        self.expire_time = config.get("expire_time")

        # Get source topic for device events
        source_topics = config.get("source_topic", {})
        self.source_topic = source_topics.get("device", "")

        # Replace {device_id} placeholder with actual device ID
        if "{device_id}" in self.source_topic:
            # If topic contains placeholder, might be sink_topic format
            sink_topics = config.get("sink_topic", {})
            device_topic = sink_topics.get("device", "")
            # For source topic, use the general subscription topic
            # Usually in format: cloud/token/in/{token}
            pass  # Use source_topic as-is

        # Parse MQTT URL
        protocol, host, port, use_ssl = self._parse_mqtt_url(self.mqtt_url)
        self.mqtt_port = port

        print(f"\n📡 Connecting to MQTT Broker")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   SSL: {use_ssl}")
        print(f"   Client ID: {self.client_id}")
        print(f"   Topic: {self.source_topic}")

        # Create MQTT client
        self.mqtt_client = mqtt.Client(client_id=self.client_id)

        # Set authentication
        self.mqtt_client.username_pw_set(self.username, self.password)

        # Configure SSL/TLS if needed
        if use_ssl:
            self.mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
            self.mqtt_client.tls_insecure_set(True)

        # Set callbacks
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        self.mqtt_client.on_message = self._on_message

        # Connect to broker
        logger.info(f"Connecting to MQTT broker: {host}:{port}")
        self.mqtt_client.connect(host, port, keepalive=60)

    def start(self):
        """
        Start MQTT monitoring loop.

        Connects to MQTT broker and starts listening for device events.
        This is a blocking call that runs until stopped.
        """
        print("\n" + "=" * 60)
        print("Starting MQTT OpenHub Event Monitoring")
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


# Global singleton instance
mqtt_openhub = TuyaMQTTOpenHub()
