"""
# MQTT Static Service - Alternative MQTT Implementation
#
# This module provides MQTT monitoring using static credentials instead of
# dynamic OpenHub API credentials. Use this if:
# 1. OpenHub API not available (free tier limitation)
# 2. Prefer manual credential management
# 3. Need simpler setup
#
# Requires manual MQTT credential setup from Tuya console.
"""

# Import the json library for parsing JSON formatted strings
import json

# Import the logging library for application logging
import logging

# Import the time library for timestamp generation and delays
import time

# Import the ssl library for configuring secure connections
import ssl

# Import Optional type hint for clearer function signatures
from typing import Optional

# Import the Paho MQTT client library for MQTT communication
import paho.mqtt.client as mqtt

# Import the TuyaConfig class to access application configuration
from config.Config import TuyaConfig

# Import alert functions to send notifications via WhatsApp
from services.whatsapp_service import (
    send_door_opened_alert,  # Function to send door opened alert
    send_door_closed_alert,  # Function to send door closed alert
    send_sensor_initialized_alert,  # Function to send initialization alert
)

# Initialize a logger for this module to track events and errors
logger = logging.getLogger(__name__)


# Define the TuyaMQTTStatic class to encapsulate MQTT functionality
class TuyaMQTTStatic:
    """
    Static MQTT client for Tuya device monitoring.

    Uses pre-configured MQTT credentials instead of dynamic API generation.
    Simpler but requires manual credential setup.
    """

    # Constructor method to initialize the class instance
    def __init__(
        self,
        mqtt_host: str = "m1-sg.iotbing.com",  # Default MQTT broker host
        mqtt_port: int = 8883,  # Default MQTT broker port (SSL)
        client_id: Optional[str] = None,  # Optional custom client ID
        username: Optional[str] = None,  # Optional custom username
        password: Optional[str] = None,  # Optional custom password
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
        # Set the device ID from the configuration
        self.device_id = TuyaConfig.DEVICE_ID

        # Initialize the last known door state to None
        self.last_door_state = None

        # MQTT connection parameters setup

        # Set the broker host
        self.mqtt_host = mqtt_host

        # Set the broker port
        self.mqtt_port = mqtt_port

        # Set the client ID, verify if provided or use default from Config
        self.client_id = client_id or TuyaConfig.ACCESS_ID

        # Set the username, verify if provided or use default from Config
        self.username = username or TuyaConfig.ACCESS_ID

        # Set the password, verify if provided or use default from Config
        self.password = password or TuyaConfig.ACCESS_SECRET

        # Construct topic for this device subscription
        # Format: tylink/{access_id}/device/status/{device_id}
        self.topic = f"tylink/{TuyaConfig.ACCESS_ID}/device/status/{self.device_id}"

        # Initialize the MQTT client attribute to None
        self.mqtt_client: Optional[mqtt.Client] = None

        # Log that the static initialization is complete
        logger.info("TuyaMQTTStatic initialized")

    # Callback method executed when the client connects to the broker
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when MQTT connection is established."""
        # Check if the connection return code (rc) is 0 (Success)
        if rc == 0:
            # Print a separator line for readability
            print("\n" + "=" * 60)
            # Print success message (no emoticons)
            print("MQTT Connection Established (Static Credentials)")
            # Print a separator line
            print("=" * 60)
            # Log the successful connection
            logger.info("MQTT connected successfully")

            # Subscribe to the specific device status topic
            client.subscribe(self.topic)
            # Print confirmation of subscription (no emoticons)
            print(f"Subscribed to topic: {self.topic}")
            # Print status message indicating waiting for events
            print("   Waiting for device events...")
            # Print a closing separator line
            print("=" * 60 + "\n")
            # Log the subscription action
            logger.info(f"Subscribed to topic: {self.topic}")
        else:
            # Dictionary mapping error codes to human-readable specific messages
            error_messages = {
                1: "Connection refused - incorrect protocol version",
                2: "Connection refused - invalid client identifier",
                3: "Connection refused - server unavailable",
                4: "Connection refused - bad username or password",
                5: "Connection refused - not authorized",
            }
            # Get the error message for the current return code, default to 'Unknown'
            error_msg = error_messages.get(rc, f"Unknown error ({rc})")
            # Print failure message with the error details
            print(f"\nMQTT Connection Failed: {error_msg}")
            # Log the connection failure
            logger.error(f"MQTT connection failed: {error_msg}")

    # Callback method executed when the client disconnects from the broker
    def _on_disconnect(self, client, userdata, rc):
        """Callback when MQTT connection is lost."""
        # Check if the disconnection was unexpected (rc != 0)
        if rc != 0:
            # Print warning message about lost connection
            print(f"\nMQTT Connection Lost (code: {rc})")
            # Print message about reconnection attempt
            print("   Will attempt to reconnect...")
            # Log the unexpected disconnection as a warning
            logger.warning(f"MQTT disconnected unexpectedly (rc={rc})")
        else:
            # Print message indicating clean disconnection
            print("\nMQTT Disconnected Cleanly")
            # Log the clean disconnection
            logger.info("MQTT disconnected")

    # Callback method executed when a message is received from the broker
    def _on_message(self, client, userdata, msg):
        """Callback when MQTT message is received."""
        try:
            # Print formatted header for received event
            print("\n" + "=" * 60)
            print("[MQTT EVENT RECEIVED]")
            print("=" * 60)

            # Parse the message payload from bytes to UTF-8 string then to JSON object
            payload = json.loads(msg.payload.decode("utf-8"))
            # Log that a message was received on a specific topic
            logger.info(f"MQTT message received on {msg.topic}")
            # Log the payload content for debugging purposes
            logger.debug(f"Payload: {json.dumps(payload, indent=2)}")

            # Extract status data from the payload
            # Tuya MQTT message format varies, try multiple patterns

            # Initialize empty list to hold status items
            status_list = []

            # Pattern 1: Check if 'status' field exists directly in payload
            if "status" in payload:
                # Get the list of status items
                status_list = payload.get("status", [])

            # Pattern 2: Check if payload is wrapped in a 'data' field
            elif "data" in payload:
                # Get the 'data' object
                data = payload.get("data", {})
                # If 'data' is a string, parse it as JSON
                if isinstance(data, str):
                    data = json.loads(data)
                # Get the list of status items from within 'data'
                status_list = data.get("status", [])

            # Initialize variables to hold extracted state
            door_state = None
            battery = None

            # Iterate through each status item in the list
            for status in status_list:
                # Get the status code (identifier)
                code = status.get("code")
                # Get the status value
                value = status.get("value")

                # Check if the code corresponds to door contact state
                if code == "doorcontact_state":
                    # Store the door state value
                    door_state = value
                    # Print the door state value
                    print(f"   doorcontact_state: {value}")
                # Check if the code corresponds to battery percentage
                elif code == "battery_percentage":
                    # Store the battery value
                    battery = value
                    # Print the battery value
                    print(f"   battery_percentage: {value}%")

            # Proceed if a valid door state was found
            if door_state is not None:
                # Get current timestamp in milliseconds
                timestamp = int(time.time() * 1000)

                # Handle initial state (first message received)
                if self.last_door_state is None:
                    # Determine text representation of state
                    state_text = "OPENED" if door_state else "CLOSED"

                    # Print initialization message
                    print(f"\n[SENSOR INITIALIZED] First event")
                    # Print current state
                    print(f"   Current state: Door {state_text}")
                    # Print timestamp
                    print(f"   Timestamp: {timestamp}")
                    # Print device ID
                    print(f"   Device ID: {self.device_id}")
                    # If battery level is known, print it
                    if battery:
                        print(f"   Battery: {battery}%")
                    # Print separator
                    print("=" * 60)

                    # Send notification that sensor is initialized
                    send_sensor_initialized_alert()
                    # Update the last known door state
                    self.last_door_state = door_state
                    # Exit the function for this message
                    return

                # Detect if the state has changed from the last known state
                if door_state != self.last_door_state:
                    # Print state change summary
                    print(
                        f"\n[DOOR STATE CHANGE] Door was {'opened' if self.last_door_state else 'closed'}, "
                        f"now {'opened' if door_state else 'closed'}"
                    )

                    # Check if the new state is True (Opened)
                    if door_state:
                        # Door opened event

                        # Print header for Open event (no emoticons)
                        print(f"DOOR OPENED (doorcontact_state = True)")
                        # Print timestamp
                        print(f"   Timestamp: {timestamp}")
                        # Print device ID
                        print(f"   Device ID: {self.device_id}")
                        # Print battery if available
                        if battery:
                            print(f"   Battery: {battery}%")
                        # Print separator
                        print("=" * 60)

                        # Send alert via WhatsApp
                        send_door_opened_alert()
                    else:
                        # Door closed event

                        # Print header for Closed event (no emoticons)
                        print(f"DOOR CLOSED (doorcontact_state = False)")
                        # Print timestamp
                        print(f"   Timestamp: {timestamp}")
                        # Print device ID
                        print(f"   Device ID: {self.device_id}")
                        # Print battery if available
                        if battery:
                            print(f"   Battery: {battery}%")
                        # Print separator
                        print("=" * 60)

                        # Send alert via WhatsApp
                        send_door_closed_alert()

                    # Update the last known state to the current state
                    self.last_door_state = door_state

        # Handle any errors during message processing
        except Exception as e:
            # Log exception with traceback
            logger.error(f"Error processing MQTT message: {e}", exc_info=True)
            # Print error message to console
            print(f"Error processing message: {e}")

    # Method to established connection to the MQTT broker
    def connect(self):
        """Connect to Tuya MQTT broker with static credentials."""
        # Print setup header
        print("\n" + "=" * 60)
        print("MQTT Static Connection Setup")
        print("=" * 60)
        # Print connection details
        print(f"   Host: {self.mqtt_host}")
        print(f"   Port: {self.mqtt_port}")
        print(f"   Client ID: {self.client_id}")
        print(f"   Topic: {self.topic}")
        print("=" * 60)

        # Create a new MQTT client instance
        self.mqtt_client = mqtt.Client(client_id=self.client_id)

        # Set username and password for authentication
        self.mqtt_client.username_pw_set(self.username, self.password)

        # Configure SSL context (insecure allowed for compatibility)
        self.mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
        # Allow insecure connections (often needed for self-signed or specific IoT certs)
        self.mqtt_client.tls_insecure_set(True)

        # Register callback functions
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_disconnect = self._on_disconnect
        self.mqtt_client.on_message = self._on_message

        # Log the connection attempt
        logger.info(f"Connecting to MQTT broker: {self.mqtt_host}:{self.mqtt_port}")
        # Print connection message (no emoticons)
        print(f"\nConnecting to {self.mqtt_host}:{self.mqtt_port}...")

        # Connect to the broker with a 60 second keepalive
        self.mqtt_client.connect(self.mqtt_host, self.mqtt_port, keepalive=60)

    # Method to start the monitoring loop
    def start(self):
        """Start MQTT monitoring loop."""
        # Print startup header
        print("\n" + "=" * 60)
        print("Starting MQTT Static Monitoring")
        print(f"Device ID: {self.device_id}")
        print("=" * 60)

        try:
            # Attempt to connect to the MQTT broker
            self.connect()

            # Print listening message
            print("\nListening for door sensor events...")
            # Print instruction to stop
            print("Press Ctrl+C to stop\n")

            # Start the blocking network loop to process callbacks
            self.mqtt_client.loop_forever()

        # Handle manual interruption (Ctrl+C)
        except KeyboardInterrupt:
            # Print stopping message (no emoticons)
            print("\n\nStopping MQTT monitoring...")
            # Call stop method to clean up
            self.stop()
        # Handle unexpected errors
        except Exception as e:
            # Log the error
            logger.error(f"Error in MQTT monitoring: {e}", exc_info=True)
            # Print error message
            print(f"\nMQTT monitoring error: {e}")
            # Re-raise the exception
            raise

    # Method to stop the monitoring loop and disconnect gracefully
    def stop(self):
        """Stop MQTT connection gracefully."""
        # Check if client exists
        if self.mqtt_client:
            # Disconnect from broker
            self.mqtt_client.disconnect()
            # Stop the background network loop
            self.mqtt_client.loop_stop()
            # Log stopped status
            logger.info("MQTT monitoring stopped")
            # Print stopped message (no emoticons)
            print("MQTT monitoring stopped")


# Create a global singleton instance of the class for the application
# Configured for Singapore Data Center (m1-sg.iotbing.com)
mqtt_static = TuyaMQTTStatic(
    mqtt_host="m1-sg.iotbing.com",
    mqtt_port=8883,
)
