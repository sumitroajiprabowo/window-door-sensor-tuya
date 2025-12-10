"""
Health Check Route - API Monitoring Endpoint

This module provides a health check endpoint for monitoring the API's
availability and operational status. Used by load balancers and monitoring
systems to verify the service is running.
"""

from flask import Blueprint
from utils.response import success_response

# Create blueprint for health check endpoints
health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint.

    Returns a simple status response to indicate the API is operational.
    This endpoint is typically called by monitoring systems, load balancers,
    or orchestration tools to verify service availability.

    Returns:
        tuple: JSON response with status "ok" and HTTP 200 status code
    """
    return success_response(data={"status": "ok"}, message="Health check passed")
