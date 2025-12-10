"""
Door Sensor Monitoring System - Main Application Entry Point

This module initializes and runs the Flask application that monitors
door sensor status via Tuya IoT Platform and sends WhatsApp alerts.
"""

from flask import Flask
from flask_cors import CORS
from config.Config import Config, TuyaConfig, WhatsAppConfig
from routes.health import health_bp
from routes.device import device_bp
import logging
import os
import sys

# Configure logging before creating Flask app to ensure proper initialization
log_level = logging.DEBUG if Config.DEBUG else logging.INFO
logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


def validate_configuration():
    """
    Validate all required configuration before starting the application.

    Checks that all required environment variables are set for both
    Tuya and WhatsApp services. This prevents runtime errors due to
    missing configuration.

    Returns:
        bool: True if all configuration is valid, False otherwise
    """
    try:
        TuyaConfig.validate()
        WhatsAppConfig.validate()
        logger.info("Configuration validation passed")
        return True
    except ValueError as e:
        logger.error(f"Configuration validation failed: {e}")
        logger.error("Please check your .env file and ensure all required variables are set")
        return False


def create_app():
    """
    Create and configure the Flask application.

    Sets up CORS and registers all route blueprints (health, device endpoints).

    Returns:
        Flask: Configured Flask application instance
    """
    flask_app = Flask(__name__)
    CORS(flask_app)

    # Register route blueprints for API endpoints
    flask_app.register_blueprint(health_bp)
    flask_app.register_blueprint(device_bp)

    return flask_app


app = create_app()


def start_listener():
    """
    Start Tuya Pulsar WebSocket Listener.

    This function initializes the Tuya Pulsar listener for real-time
    device status updates via WebSocket. It should only be called in
    the main process, not in Flask's reloader process.

    Note: Currently disabled in favor of HTTP polling due to encryption issues.
    """
    print("\n" + "=" * 60)
    print("Initializing Tuya Listener...")
    print("=" * 60)

    try:
        print("Importing tuya_listener...")
        from services.tuya_listener import tuya_listener

        print("Calling tuya_listener.start()...")
        tuya_listener.start()

        print("Tuya Listener started successfully")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\nERROR: Failed to start Tuya Listener!")
        print(f"Exception: {e}")
        print("=" * 60)
        import traceback

        traceback.print_exc()
        print("=" * 60 + "\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Door Sensor Monitoring System")
    print(f"Environment: {Config.ENV}")
    print(f"Debug Mode: {Config.DEBUG}")
    print("=" * 60 + "\n")

    # Validate all required configuration before starting
    if not validate_configuration():
        logger.error("Exiting due to configuration errors")
        sys.exit(1)

    # Determine if we're in the Flask reloader's child process
    # This prevents starting the monitor twice in debug mode
    is_reloader_child = os.environ.get("WERKZEUG_RUN_MAIN") == "true"
    is_debug = Config.DEBUG

    # Start the door sensor monitor
    # In debug mode, only start in child process; otherwise always start
    if is_reloader_child or not is_debug:
        logger.info("Starting Door Sensor Monitor...")

        # Use HTTP Polling service as the primary monitoring method
        # This is more reliable than Pulsar WebSocket for our use case
        from services.polling_service import door_poller

        door_poller.start()

        # Alternative: Pulsar WebSocket listener (currently disabled)
        # Uncomment below if Pulsar encryption issues are resolved
        # start_listener()
    else:
        logger.info("Skipping monitor start (parent reloader process)")

    # Start Flask web server
    logger.info(f"Starting Flask server on {Config.HOST}:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
