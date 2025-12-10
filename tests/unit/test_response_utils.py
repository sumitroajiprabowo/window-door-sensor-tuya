"""
Unit tests for utils/response.py module.

Tests response utility functions for standardized API responses.
"""

import pytest
import json


@pytest.fixture
def app_context():
    """Create Flask app context for testing."""
    from main import create_app

    app = create_app()
    with app.app_context():
        yield app


class TestSuccessResponse:
    """Test cases for success_response function."""

    def test_success_response_default_values(self, app_context):
        """Test success response with default message and status code."""
        from utils.response import success_response

        response, status_code = success_response()

        assert status_code == 200
        response_data = json.loads(response.get_data(as_text=True))
        assert response_data["status"] == "success"
        assert response_data["message"] == "Success"
        assert response_data["result"] is None

    def test_success_response_with_data(self, app_context):
        """Test success response with custom data."""
        from utils.response import success_response

        test_data = {"device_id": "123", "status": "online"}
        response, status_code = success_response(data=test_data)

        assert status_code == 200
        response_data = json.loads(response.get_data(as_text=True))
        assert response_data["status"] == "success"
        assert response_data["result"] == test_data

    def test_success_response_with_custom_message(self, app_context):
        """Test success response with custom message."""
        from utils.response import success_response

        custom_message = "Device updated successfully"
        response, status_code = success_response(message=custom_message)

        response_data = json.loads(response.get_data(as_text=True))
        assert response_data["message"] == custom_message

    def test_success_response_with_custom_status_code(self, app_context):
        """Test success response with custom status code."""
        from utils.response import success_response

        response, status_code = success_response(status_code=201)

        assert status_code == 201

    def test_success_response_with_list_data(self, app_context):
        """Test success response with list data."""
        from utils.response import success_response

        test_data = [
            {"code": "doorcontact_state", "value": True},
            {"code": "battery_percentage", "value": 85},
        ]
        response, status_code = success_response(data=test_data)

        response_data = json.loads(response.get_data(as_text=True))
        assert response_data["result"] == test_data
        assert isinstance(response_data["result"], list)

    def test_success_response_with_all_parameters(self, app_context):
        """Test success response with all parameters specified."""
        from utils.response import success_response

        test_data = {"id": 456}
        test_message = "Operation completed"
        test_status = 202

        response, status_code = success_response(
            data=test_data, message=test_message, status_code=test_status
        )

        assert status_code == test_status
        response_data = json.loads(response.get_data(as_text=True))
        assert response_data["status"] == "success"
        assert response_data["message"] == test_message
        assert response_data["result"] == test_data

    def test_success_response_content_type(self, app_context):
        """Test that success response has correct content type."""
        from utils.response import success_response

        response, _ = success_response()

        assert response.content_type == "application/json"


class TestErrorResponse:
    """Test cases for error_response function."""

    def test_error_response_default_values(self, app_context):
        """Test error response with default message and status code."""
        from utils.response import error_response

        response, status_code = error_response()

        assert status_code == 400
        response_data = json.loads(response.get_data(as_text=True))
        assert response_data["status"] == "error"
        assert response_data["message"] == "Error"
        assert "details" not in response_data

    def test_error_response_with_custom_message(self, app_context):
        """Test error response with custom message."""
        from utils.response import error_response

        custom_message = "Device not found"
        response, status_code = error_response(message=custom_message)

        response_data = json.loads(response.get_data(as_text=True))
        assert response_data["message"] == custom_message

    def test_error_response_with_custom_status_code(self, app_context):
        """Test error response with custom status code."""
        from utils.response import error_response

        response, status_code = error_response(status_code=404)

        assert status_code == 404

    def test_error_response_with_details(self, app_context):
        """Test error response with additional details."""
        from utils.response import error_response

        error_details = {"field": "device_id", "error": "required"}
        response, status_code = error_response(details=error_details)

        response_data = json.loads(response.get_data(as_text=True))
        assert response_data["details"] == error_details

    def test_error_response_with_all_parameters(self, app_context):
        """Test error response with all parameters specified."""
        from utils.response import error_response

        test_message = "Validation failed"
        test_status = 422
        test_details = {"errors": ["Invalid format"]}

        response, status_code = error_response(
            message=test_message, status_code=test_status, details=test_details
        )

        assert status_code == test_status
        response_data = json.loads(response.get_data(as_text=True))
        assert response_data["status"] == "error"
        assert response_data["message"] == test_message
        assert response_data["details"] == test_details

    def test_error_response_500_status(self, app_context):
        """Test error response for internal server error."""
        from utils.response import error_response

        response, status_code = error_response(
            message="Internal Server Error", status_code=500
        )

        assert status_code == 500
        response_data = json.loads(response.get_data(as_text=True))
        assert response_data["status"] == "error"
        assert response_data["message"] == "Internal Server Error"

    def test_error_response_401_unauthorized(self, app_context):
        """Test error response for unauthorized access."""
        from utils.response import error_response

        response, status_code = error_response(message="Unauthorized", status_code=401)

        assert status_code == 401
        response_data = json.loads(response.get_data(as_text=True))
        assert response_data["message"] == "Unauthorized"

    def test_error_response_content_type(self, app_context):
        """Test that error response has correct content type."""
        from utils.response import error_response

        response, _ = error_response()

        assert response.content_type == "application/json"

    def test_error_response_without_details(self, app_context):
        """Test that details field is not included when not provided."""
        from utils.response import error_response

        response, _ = error_response(message="Test error")

        response_data = json.loads(response.get_data(as_text=True))
        assert "details" not in response_data
        assert "status" in response_data
        assert "message" in response_data
