#!/usr/bin/env python3
"""
Debug Pulsar Connection - Shows raw messages received
"""
import os
import time
import logging
from dotenv import load_dotenv
from tuya_connector import TuyaOpenPulsar, TuyaCloudPulsarTopic

load_dotenv()

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

ACCESS_ID = os.getenv("TUYA_ACCESS_ID")
ACCESS_SECRET = os.getenv("TUYA_ACCESS_SECRET")
ENDPOINT = os.getenv("TUYA_PULSAR_ENDPOINT")
DEVICE_ID = os.getenv("DEVICE_ID")

print("\n" + "=" * 70)
print("TUYA PULSAR DEBUG - RAW MESSAGE MONITORING")
print("=" * 70)
print(f"Endpoint: {ENDPOINT}")
print(f"Access ID: {ACCESS_ID}")
print(f"Device ID: {DEVICE_ID}")
print("=" * 70)
print("\nConnecting to Pulsar...")
print("Waiting for messages (try opening/closing door now)...")
print("Press Ctrl+C to stop\n")

message_count = 0


def on_message(msg):
    global message_count
    message_count += 1

    print("\n" + "=" * 68)
    print(f"MESSAGE #{message_count} RECEIVED")
    print("=" * 70)
    print(msg)
    print("=" * 70 + "\n")


def on_error(error):
    print(f"\nERROR: {error}\n")
    if "401" in str(error):
        print("Authentication failed! Check Message Service subscription.\n")


def on_close():
    print("\nConnection closed\n")


try:
    pulsar = TuyaOpenPulsar(
        ACCESS_ID,
        ACCESS_SECRET,
        ENDPOINT,
        TuyaCloudPulsarTopic.TEST,  # Use TEST topic to match test environment
    )

    pulsar.add_message_listener(on_message)

    print("Connection established!")
    print("Listening for events...\n")

    pulsar.start()

    # Keep running
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    print("\n\nStopping...")
    print(f"Total messages received: {message_count}")
except Exception as e:
    print(f"\nException: {e}")
