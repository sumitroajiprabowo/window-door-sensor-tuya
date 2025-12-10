"""
WhatsApp Service - Notification Integration

This module handles sending WhatsApp notifications through the WhatsApp
Business API when door sensor events are detected. It provides functions
to send custom messages and predefined alerts for door state changes.
"""

import requests
import logging
from requests.auth import HTTPBasicAuth
from config.Config import WhatsAppConfig


def send_whatsapp_message(message: str) -> bool:
    """
    Send a WhatsApp message via the WhatsApp Business API.

    Sends a text message to a configured WhatsApp group when door sensor
    state changes are detected. Uses HTTP Basic Authentication to access
    the WhatsApp API endpoint.

    Args:
        message (str): The message text to send. Typically, door status
            messages like "DOOR ID OPEN" (server door opened) or
            "DOOR IS CLOSES" (server door closed).

    Returns:
        bool: True if message was sent successfully, False if an error occurred
    """
    url = WhatsAppConfig.API_URL
    auth = HTTPBasicAuth(WhatsAppConfig.API_USER, WhatsAppConfig.API_PASSWORD)
    headers = {"Content-Type": "application/json"}

    # Prepare API payload with message details
    payload = {"phone": WhatsAppConfig.GROUP_ID, "message": message}

    # Add optional parameters if configured
    if WhatsAppConfig.IS_FORWARDED:
        payload["is_forwarded"] = True

    # Add duration only if it's non-zero
    if WhatsAppConfig.DURATION > 0:
        payload["duration"] = WhatsAppConfig.DURATION

    try:
        logging.info(f"Sending WhatsApp message: '{message}'")
        logging.debug(f"   URL: {url}")
        logging.debug(f"   Group: {WhatsAppConfig.GROUP_ID}")

        # Send POST request to WhatsApp API
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            auth=auth,
            timeout=10,  # 10 second timeout to prevent hanging
        )
        response.raise_for_status()

        logging.info(
            f"WhatsApp message sent successfully (HTTP {response.status_code})"
        )
        return True

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send WhatsApp message: {e}")
        if hasattr(e, "response") and e.response is not None:
            logging.error(f"   Response: {e.response.text}")
        return False


def send_door_opened_alert() -> bool:
    """
    Send WhatsApp alert when door is opened.

    Sends a configurable message (from WA_MESSAGE_DOOR_OPENED environment
    variable) when the door sensor detects an open state. The message can
    be customized via environment configuration to suit different use cases.

    Returns:
        bool: True if alert was sent successfully, False otherwise
    """
    return send_whatsapp_message(WhatsAppConfig.MESSAGE_DOOR_OPENED)


def send_door_closed_alert() -> bool:
    """
    Send WhatsApp alert when door is closed.

    Sends a configurable message (from WA_MESSAGE_DOOR_CLOSED environment
    variable) when the door sensor detects a closed state. The message can
    be customized via environment configuration to suit different use cases.

    Returns:
        bool: True if alert was sent successfully, False otherwise
    """
    return send_whatsapp_message(WhatsAppConfig.MESSAGE_DOOR_CLOSED)


def send_sensor_initialized_alert() -> bool:
    """
    Send WhatsApp alert when sensor monitoring is initialized.

    Sends a configurable message (from WA_MESSAGE_SENSOR_INITIALIZED environment
    variable) when the monitoring service first starts and detects the initial
    sensor state. This prevents false alarms from server restarts.

    Returns:
        bool: True if alert was sent successfully, False otherwise
    """
    return send_whatsapp_message(WhatsAppConfig.MESSAGE_SENSOR_INITIALIZED)
