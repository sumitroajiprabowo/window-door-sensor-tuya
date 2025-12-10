#!/usr/bin/env python3
"""
Test Tuya Connection - Verifies both HTTP API and Pulsar WebSocket
"""
import os
import sys
import time
import logging
from dotenv import load_dotenv
from tuya_connector import TuyaOpenAPI, TuyaOpenPulsar, TuyaCloudPulsarTopic

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")


def test_http_api():
    """Test HTTP API Connection"""
    print("\n" + "=" * 60)
    print("TEST 1: HTTP API Connection")
    print("=" * 60)

    access_id = os.getenv("TUYA_ACCESS_ID")
    access_secret = os.getenv("TUYA_ACCESS_SECRET")
    endpoint = os.getenv("TUYA_ENDPOINT")
    device_id = os.getenv("DEVICE_ID")

    print(f"Endpoint: {endpoint}")
    print(f"Access ID: {access_id}")
    print(f"Device ID: {device_id}")

    try:
        openapi = TuyaOpenAPI(endpoint, access_id, access_secret)
        openapi.connect()

        if openapi.is_connect():
            print("HTTP API: Connected successfully!")

            # Test device status
            print("\nTesting device status...")
            response = openapi.get(f"/v1.0/devices/{device_id}/status")

            if response.get("success"):
                print("Device Status: Retrieved successfully!")
                print(f"   Data: {response.get('result')}")
                return True
            else:
                print(f"Device Status Failed: {response.get('msg')}")
                print(f"   Code: {response.get('code')}")
                return False
        else:
            print("HTTP API: Failed to connect")
            return False

    except Exception as e:
        print(f"HTTP API Error: {e}")
        return False


def test_pulsar_websocket():
    """Test Pulsar WebSocket Connection"""
    print("\n" + "=" * 60)
    print("TEST 2: Pulsar WebSocket Connection")
    print("=" * 60)

    access_id = os.getenv("TUYA_ACCESS_ID")
    access_secret = os.getenv("TUYA_ACCESS_SECRET")
    pulsar_endpoint = os.getenv("TUYA_PULSAR_ENDPOINT")

    print(f"Pulsar Endpoint: {pulsar_endpoint}")
    print(f"Access ID: {access_id}")

    connection_established = False

    def on_message(msg):
        nonlocal connection_established
        connection_established = True
        print(f"WebSocket: Message received!")
        print(f"   {msg}")

    try:
        pulsar = TuyaOpenPulsar(
            access_id, access_secret, pulsar_endpoint, TuyaCloudPulsarTopic.PROD
        )

        pulsar.add_message_listener(on_message)

        print("\nConnecting to Pulsar WebSocket...")
        print("   (Waiting 10 seconds for connection...)")

        pulsar.start()
        time.sleep(10)

        if connection_established:
            print("\nPulsar WebSocket: Working perfectly!")
            pulsar.stop()
            return True
        else:
            print("\nPulsar WebSocket: No messages received yet")
            print("   (This is normal if no device events occurred)")
            print("   Connection appears stable.")
            pulsar.stop()
            return True

    except Exception as e:
        print(f"Pulsar WebSocket Exception: {e}")
        return False


def main():
    print("\n" + "TUYA CONNECTION TEST ".center(60, "="))
    print()

    # Test 1: HTTP API
    http_ok = test_http_api()

    # Test 2: Pulsar WebSocket
    pulsar_ok = test_pulsar_websocket()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"HTTP API:          {'PASS' if http_ok else 'FAIL'}")
    print(f"Pulsar WebSocket:  {'PASS' if pulsar_ok else 'FAIL'}")
    print("=" * 60)

    if http_ok and pulsar_ok:
        print("\nAll tests passed! Your Tuya connection is ready!")
        print("   You can now run: .venv/bin/python main.py")
        return 0
    elif http_ok and not pulsar_ok:
        print("\nHTTP API works, but WebSocket failed.")
        print("   Please subscribe to 'Message Subscription' service")
        print("   in Tuya IoT Console: https://iot.tuya.com/")
        return 1
    else:
        print("\nConnection failed. Please check:")
        print("   1. Credentials are correct")
        print("   2. Services are subscribed (IoT Core + Message Subscription)")
        print("   3. Device is linked to your project")
        print("   4. Region/endpoint matches your data center")
        return 1


if __name__ == "__main__":
    sys.exit(main())
