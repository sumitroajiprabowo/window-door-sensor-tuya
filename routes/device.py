"""
Device Routes - Tuya Device Management API Endpoints

This module provides REST API endpoints for interacting with Tuya IoT devices.
Supports querying device status and sending control commands to devices.
"""

from flask import Blueprint, request
from services.tuya_service import tuya_service
from utils.response import success_response, error_response
import logging

# Create blueprint for device management endpoints
device_bp = Blueprint("device", __name__)


@device_bp.route("/devices/<device_id>/status", methods=["GET"])
def get_device_status(device_id):
    """
    Get current status of a Tuya device.

    Retrieves all current status values for the specified device including
    sensor readings, battery level, and other device properties.

    Args:
        device_id (str): The unique identifier of the Tuya device

    Returns:
        tuple: JSON response containing device status data and HTTP status code

    Example Response:
        {
            "status": "success",
            "message": "Success",
            "result": [
                {"code": "doorcontact_state", "value": false},
                {"code": "battery_percentage", "value": 85}
            ]
        }
    """
    try:
        # Query Tuya Cloud API for device status
        response = tuya_service.get_device_status(device_id)

        if response.get("success"):
            return success_response(data=response.get("result"))
        else:
            return error_response(
                message=response.get("msg", "Failed to fetch status"),
                status_code=response.get("code", 500),
            )
    except Exception as e:
        logging.error(f"Error fetching device status: {e}")
        return error_response(message="Internal Server Error", status_code=500)


@device_bp.route("/devices/<device_id>/commands", methods=["POST"])
def send_device_command(device_id):
    """
    Send control commands to a Tuya device.

    Accepts a list of commands to execute on the specified device.
    Commands can control device behavior, update settings, or trigger actions.

    Args:
        device_id (str): The unique identifier of the Tuya device

    Request Body:
        {
            "commands": [
                {"code": "switch", "value": true},
                {"code": "brightness", "value": 75}
            ]
        }

    Returns:
        tuple: JSON response indicating command execution status and HTTP status code

    Example Response:
        {
            "status": "success",
            "message": "Command sent successfully",
            "result": {...}
        }
    """
    try:
        # Parse request body
        data = request.get_json(silent=True)

        # Validate request body contains commands
        if not data or "commands" not in data:
            return error_response(message="Invalid request body", status_code=400)

        # Extract commands list
        commands = data["commands"]

        # Send commands to device via Tuya Cloud API
        response = tuya_service.send_command(device_id, commands)

        if response.get("success"):
            return success_response(
                data=response.get("result"), message="Command sent successfully"
            )
        else:
            return error_response(
                message=response.get("msg", "Failed to send command"),
                status_code=response.get("code", 500),
            )
    except Exception as e:
        logging.error(f"Error sending command: {e}")
        return error_response(message="Internal Server Error", status_code=500)
