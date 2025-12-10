import os
import time
import logging
from dotenv import load_dotenv
from tuya_connector import TuyaOpenPulsar, TuyaCloudPulsarTopic

load_dotenv()

ACCESS_ID = os.getenv("TUYA_ACCESS_ID")
ACCESS_SECRET = os.getenv("TUYA_ACCESS_SECRET")

# List of Tuya Pulsar Endpoints by Region
ENDPOINTS = {
    "CN (China)": "wss://mqe.tuyacn.com:8285/",
    "US (Western America)": "wss://mqe.tuyaus.com:8285/",
    "EU (Central Europe)": "wss://mqe.tuyaeu.com:8285/",
    "IN (India)": "wss://mqe.tuyain.com:8285/",
    "WE (Western Europe)": "wss://mqe.tuyawe.com:8285/",
    "UE (Eastern America)": "wss://mqe.tuyaue.com:8285/",
    "SG (Singapore - Legacy)": "wss://mqe.tuyaas.com:8285/",
    "SG (Singapore - IotBing)": "wss://mqe-sg.iotbing.com:8285/",
}

logging.basicConfig(level=logging.INFO, format="%(message)s")


def test_connection():
    if not ACCESS_ID or not ACCESS_SECRET:
        print("Error: TUYA_ACCESS_ID or TUYA_ACCESS_SECRET not found in .env")
        return

    print(f"Testing credentials for Access ID: {ACCESS_ID}...")

    success_endpoint = None

    for region, endpoint in ENDPOINTS.items():
        print(f"\nTesting Region: {region} - {endpoint}")

        # We need a way to check if connected without blocking forever.
        # TuyaOpenPulsar starts a thread. We can check if it stays alive or errors.

        # However, TuyaOpenPulsar doesn't expose a simple "connect_test".
        # We will try to start it and see if it throws a 401 immediately.

        try:
            pulsar = TuyaOpenPulsar(
                ACCESS_ID, ACCESS_SECRET, endpoint, TuyaCloudPulsarTopic.PROD
            )

            # Monkey patch error handler to capture success/fail
            connection_status = {"connected": False, "error": None}

            def custom_on_error(ws, error):
                connection_status["error"] = error

            def custom_on_open(ws):
                connection_status["connected"] = True

            pulsar._on_error = custom_on_error
            pulsar._on_open = custom_on_open  # This might not be standard in TuyaOpenPulsar class but in the websocket app

            # Since TuyaOpenPulsar wraps websocket.WebSocketApp, let's try to access it?
            # Actually, let's just run it for 3 seconds.

            pulsar.start()  # Starts in thread

            time.sleep(3)  # Wait for handshake

            if connection_status.get("error"):
                print(f"   Failed: {connection_status['error']}")
                pulsar.stop()
                continue

            # If we are here, we might have connected or still connecting.
            # Looking at logs `Handshake status 401` usually prints to stderr.
            # This script relies on visual confirmation or the absence of the 401 loop.

            print(f"   Check logs above. If no 401, this might be the one.")
            pulsar.stop()

        except Exception as e:
            print(f"   Exception: {e}")


if __name__ == "__main__":
    test_connection()
