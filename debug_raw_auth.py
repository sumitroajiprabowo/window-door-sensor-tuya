import hashlib
import json
import logging
import threading
import time
import os
import websocket
from dotenv import load_dotenv

load_dotenv()

# Configuration
ACCESS_ID = os.getenv("TUYA_ACCESS_ID")
ACCESS_SECRET = os.getenv("TUYA_ACCESS_SECRET")
ENDPOINT = os.getenv("TUYA_PULSAR_ENDPOINT", "wss://mqe-sg.iotbing.com:8285/")
TOPIC = "event"  # PROD


def _gen_pwd(access_id, access_secret):
    """Generates the password for Tuya Pulsar auth"""
    md5_hex = hashlib.md5(
        access_id.encode("utf-8")
        + hashlib.md5(access_secret.encode("utf-8")).hexdigest().encode("utf-8")
    ).hexdigest()
    return md5_hex[8:24]


def _get_topic_url(url, access_id, topic):
    """Constructs the subscription URL"""
    return url + f"ws/v2/consumer/persistent/{access_id}/out/{topic}/{access_id}-sub"


def debug_auth():
    if not ACCESS_ID or not ACCESS_SECRET:
        print("Error: Credentials missing in .env")
        return

    print(f"Debugging Tuya Pulsar Auth")
    print(f"   Endpoint: {ENDPOINT}")
    print(f"   Access ID: {ACCESS_ID}")

    # Generate Password
    pwd = _gen_pwd(ACCESS_ID, ACCESS_SECRET)
    print(f"   Generated Password (MD5 partial): {pwd}")

    # Construct URL
    ws_url = _get_topic_url(ENDPOINT, ACCESS_ID, TOPIC)
    print(f"   Connection URL: {ws_url}")

    # Define Handlers
    def on_message(ws, message):
        print(f"   Received Message: {message}")

    def on_error(ws, error):
        print(f"   Error: {error}")

    def on_close(ws, close_status_code, close_msg):
        print(f"   Closed: {close_status_code} - {close_msg}")

    def on_open(ws):
        print("   Connected! Handshake Successful.")
        print("   (Closing connection in 2 seconds...)")
        time.sleep(2)
        ws.close()

    # Create Websocket App with explicit Auth
    # Tuya Pulsar uses Basic Auth? Or query params?
    # Source code implies it puts it in the URL or headers?
    # Actually, looking at openpulsar.py typically:
    # It might use headers or just the password logic.
    # Wait, the official SDK/connector might use `username` and `password` for the WS connection.
    # Let's verify how TuyaOpenPulsar does it.

    # In TuyaOpenPulsar.start():
    # self.ws_app = websocket.WebSocketApp(self.topic_url, ... header={"username": self.access_id, "password": self.gen_pwd()})
    # Aha! It uses HEADERS or subprotocols? No, usually arguments to WebSocketApp.
    # But standard WebSocketApp doesn't take 'username' arg, it takes 'header'.
    # Let's try headers.

    headers = {"username": ACCESS_ID, "password": pwd}

    # Some older Tuya docs say keys for pulsar are different.
    # But tuya-connector-python uses the above logic.

    ws = websocket.WebSocketApp(
        ws_url,
        header=headers,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    print("\nConnecting...")
    ws.run_forever()


if __name__ == "__main__":
    debug_auth()
