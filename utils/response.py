"""
Response Utilities - Standardized API Response Formatting

This module provides utility functions for creating consistent JSON responses
across all API endpoints. Ensures uniform response structure for both
successful and error responses.
"""

from flask import jsonify


def success_response(data=None, message="Success", status_code=200):
    """
    Create a standardized success response.

    Generates a JSON response with a consistent structure for successful
    API operations. All success responses include a status field set to
    "success", an optional message, and the result data.

    Args:
        data: The data to include in the response (typically a dict or list)
        message (str): Success message describing the operation. Defaults to "Success"
        status_code (int): HTTP status code. Defaults to 200 (OK)

    Returns:
        tuple: Flask Response object with JSON data and HTTP status code

    Example:
        >>> success_response(data={"id": 123}, message="Device found")
        ({"status": "success", "message": "Device found", "result": {"id": 123}}, 200)
    """
    response = {"status": "success", "message": message, "result": data}
    return jsonify(response), status_code


def error_response(message="Error", status_code=400, details=None):
    """
    Create a standardized error response.

    Generates a JSON response with a consistent structure for error
    conditions. All error responses include a status field set to "error"
    and a descriptive message. Optional details can provide additional
    context about the error.

    Args:
        message (str): Error message describing what went wrong. Defaults to "Error"
        status_code (int): HTTP status code. Defaults to 400 (Bad Request)
        details: Optional additional error information (e.g., validation errors)

    Returns:
        tuple: Flask Response object with JSON data and HTTP status code

    Example:
        >>> error_response(message="Device not found", status_code=404)
        ({"status": "error", "message": "Device not found"}, 404)
    """
    response = {
        "status": "error",
        "message": message,
    }
    # Include additional details if provided
    if details:
        response["details"] = details
    return jsonify(response), status_code
