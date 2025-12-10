"""
Tuya Listener - WebSocket-based Real-time Event Monitoring

This module implements real-time monitoring of Tuya IoT devices using
the Pulsar WebSocket protocol. It subscribes to device events and
processes them as they occur.

Note: Currently disabled in favor of HTTP polling due to encryption issues.
"""
import logging
import json
from tuya_connector import TuyaOpenPulsar, TuyaCloudPulsarTopic
from config.Config import TuyaConfig
from services.whatsapp_service import send_door_opened_alert, send_door_closed_alert


class TuyaListener:
    """
    WebSocket-based listener for real-time Tuya device events.

    This class establishes a WebSocket connection to the Tuya Pulsar service
    to receive real-time notifications when device status changes occur.
    It provides instant event detection without polling overhead.

    Note: This approach requires proper encryption handling and network
    configuration which may not work in all environments.
    """

    def __init__(self):
        """
        Initialize the Tuya Pulsar listener.

        Sets up WebSocket connection parameters and registers message
        and error handlers for processing incoming events.
        """
        self.access_id = TuyaConfig.ACCESS_ID
        self.access_secret = TuyaConfig.ACCESS_SECRET
        self.endpoint = TuyaConfig.TUYA_PULSAR_ENDPOINT

        # Initialize Pulsar WebSocket client
        # Using PROD topic for production environment events
        self.open_pulsar = TuyaOpenPulsar(
            self.access_id, self.access_secret, self.endpoint, TuyaCloudPulsarTopic.PROD
        )
        self.open_pulsar.add_message_listener(self.on_message)

        # Store endpoint for error logging
        self.pulsar_endpoint = self.endpoint

    def handle_websocket_error(self, error):
        """
        Handle WebSocket connection errors.

        Detects authentication failures (401) and logs detailed error
        information to help diagnose configuration issues.

        Args:
            error: Error object or message from the WebSocket connection
        """
        # Check for authentication failures
        if "401" in str(error) or "Unauthorized" in str(error):
            logging.error(
                f"Tuya Pulsar Authentication Failed (401). Stopping listener. "
                f"Check your ACCESS_ID, ACCESS_SECRET, and REGION ENDPOINT ({self.pulsar_endpoint})."
            )

    def on_message(self, msg):  # pylint: disable=no-self-use
        """
        Message callback handler for Pulsar WebSocket events.

        Processes incoming messages from the Tuya Pulsar service and handles
        device status updates. Supports multiple message protocols:
        - Protocol 1000: bizData format with properties array (newer)
        - Protocol 4: status format with status array (older)

        Filters messages to only process events from the configured device
        and sends WhatsApp alerts when door state changes are detected.

        Note: This method is registered as a callback and cannot be static
        even though it doesn't use instance variables directly.

        Args:
            msg (str): JSON-formatted message from Tuya Pulsar
        """
        try:
            print(f"\n[on_message] Message received from Pulsar!")
            logging.debug(f"Raw message received: {msg}")

            # Parse JSON payload
            payload = json.loads(msg)
            data = payload.get("data")
            if not data:
                print("WARNING: No 'data' field in message, skipping")
                logging.debug("No 'data' field in message, skipping")
                return

            # Extract device ID and status based on message format
            #  1: Protocol 1000 with bizData (newer format)
            if "bizData" in data:
                biz_data = data.get("bizData", {})
                device_id = biz_data.get("devId")
                properties = biz_data.get("properties", [])
                timestamp = data.get("ts")

                status_list = properties
                logging.debug(f"Protocol 1000 format detected: {len(properties)} properties")

            # Format 2: Protocol 4 with status (older format)
            elif "devId" in data:
                device_id = data.get("devId")
                status_list = data.get("status", [])
                timestamp = data.get("t")
                logging.debug(f"Protocol 4 format detected: {len(status_list)} status items")

            else:
                logging.debug(f"Unknown message format: {data.keys()}")
                return

            # Validate device ID
            if not device_id:
                logging.debug("No device ID found in message")
                return

            # Filter messages to only process our target device
            if device_id != TuyaConfig.DEVICE_ID:
                logging.debug(f"Ignored message from different device: {device_id}")
                return

            # Process status updates from our target device
            print(f"Event from device: {device_id}")
            logging.info(f"Event from device: {device_id}")

            # Iterate through status updates
            for status in status_list:
                code = status.get("code")
                value = status.get("value")

                if code == "doorcontact_state":
                    # Extract timestamp from various possible fields
                    status_timestamp = status.get("time") or status.get("t") or timestamp or "N/A"

                    if value:
                        # Door opened event
                        print(f"DOOR OPENED (doorcontact_state = True)")
                        print(f"   Timestamp: {status_timestamp}")
                        print(f"   Device ID: {device_id}")
                        logging.warning("DOOR OPENED (doorcontact_state = True)")
                        logging.info(f"   Timestamp: {status_timestamp}")
                        logging.info(f"   Device ID: {device_id}")

                        # Trigger WhatsApp notification
                        send_door_opened_alert()
                    else:
                        # Door closed event
                        print(f"DOOR CLOSED (doorcontact_state = False)")
                        print(f"   Timestamp: {status_timestamp}")
                        print(f"   Device ID: {device_id}")
                        logging.info("DOOR CLOSED (doorcontact_state = False)")
                        logging.info(f"   Timestamp: {status_timestamp}")
                        logging.info(f"   Device ID: {device_id}")

                        # Trigger WhatsApp notification
                        send_door_closed_alert()

                elif code == "battery_percentage":
                    # Log battery level updates
                    logging.info(f"Battery: {value}%")
                else:
                    # Log other status updates at debug level
                    logging.debug(f"Status update - {code}: {value}")

        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON message: {e}")
        except Exception as e:
            logging.error(f"Error processing message: {e}")
            logging.debug(f"Message content: {msg}")

    def start(self):
        """
        Start the Pulsar WebSocket listener.

        Validates credentials, establishes WebSocket connection, and begins
        listening for real-time device events. Performs pre-flight checks
        to ensure configuration is valid before attempting connection.
        """
        print("\n[tuya_listener.start()] Function called")
        print(f"Access ID: {self.access_id[:10]}..." if self.access_id else "ERROR: No Access ID")
        print(f"Access Secret: {'*' * 10}" if self.access_secret else "ERROR: No Secret")

        # Validate credentials are configured
        if not self.access_id or not self.access_secret or self.access_id == "your_access_id":
            print("WARNING: Tuya Access ID/Secret not found. Listener will NOT start.")
            logging.warning(
                "WARNING: Tuya Access ID/Secret not found. Webhook listener will NOT start."
            )
            return

        # Verify credentials work via HTTP API before starting WebSocket
        print("Checking Tuya credentials via HTTP API...")
        from services.tuya_service import tuya_service

        if not tuya_service.is_authenticated():
            print("ERROR: Tuya credentials invalid (HTTP auth failed). Listener will NOT start.")
            logging.error(
                "ERROR: Tuya credentials invalid (HTTP auth failed). Webhook listener will NOT start."
            )
            return

        print("Tuya credentials validated successfully!")

        from config.Config import WhatsAppConfig

        # Display configuration summary
        print("\n" + "=" * 60)
        print("Starting Tuya Pulsar Listener...")
        print(f"Endpoint: {self.endpoint}")
        print(f"Monitoring Device: {TuyaConfig.DEVICE_ID}")
        print(f"Topic: PROD Environment")
        print(f"WhatsApp Group: {WhatsAppConfig.GROUP_ID}")
        print(f"WhatsApp API: {WhatsAppConfig.API_URL}")
        print("=" * 60)
        print("Waiting for door/window sensor events...")
        print("Legend: Door Opened | Door Closed | Battery")
        print("=" * 60 + "\n")

        # Establish WebSocket connection
        print("Connecting to Pulsar WebSocket...")
        self.open_pulsar.start()
        print("Pulsar connection started!")


# Global singleton instance for application-wide use
tuya_listener = TuyaListener()
