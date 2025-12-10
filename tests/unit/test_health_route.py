"""
Unit tests for routes/health.py module.

Tests health check endpoint functionality.
"""

import pytest
import json


class TestHealthRoute:
    """Test cases for health check endpoint."""

    def test_health_check_success(self, flask_test_client):
        """Test that health check returns success response."""
        response = flask_test_client.get("/health")

        assert response.status_code == 200

    def test_health_check_json_response(self, flask_test_client):
        """Test that health check returns JSON response."""
        response = flask_test_client.get("/health")

        assert response.content_type == "application/json"

    def test_health_check_status_ok(self, flask_test_client):
        """Test that health check returns status ok."""
        response = flask_test_client.get("/health")
        data = json.loads(response.get_data(as_text=True))

        assert data["status"] == "success"
        assert data["result"]["status"] == "ok"

    def test_health_check_message(self, flask_test_client):
        """Test that health check returns correct message."""
        response = flask_test_client.get("/health")
        data = json.loads(response.get_data(as_text=True))

        assert data["message"] == "Health check passed"

    def test_health_check_structure(self, flask_test_client):
        """Test that health check response has correct structure."""
        response = flask_test_client.get("/health")
        data = json.loads(response.get_data(as_text=True))

        # Verify all expected keys are present
        assert "status" in data
        assert "message" in data
        assert "result" in data
        assert "status" in data["result"]

    def test_health_check_method_not_allowed(self, flask_test_client):
        """Test that only GET method is allowed for health check."""
        response = flask_test_client.post("/health")

        assert response.status_code == 405  # Method Not Allowed

    def test_health_check_multiple_calls(self, flask_test_client):
        """Test that health check is idempotent."""
        response1 = flask_test_client.get("/health")
        response2 = flask_test_client.get("/health")

        assert response1.status_code == 200
        assert response2.status_code == 200

        data1 = json.loads(response1.get_data(as_text=True))
        data2 = json.loads(response2.get_data(as_text=True))

        assert data1 == data2
