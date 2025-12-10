from tuya_connector import TuyaOpenAPI
import os
import json
from dotenv import load_dotenv
import logging

load_dotenv()

ACCESS_ID = os.getenv("TUYA_ACCESS_ID")
ACCESS_SECRET = os.getenv("TUYA_ACCESS_SECRET")
ENDPOINT = os.getenv("TUYA_ENDPOINT")
DEVICE_ID = os.getenv("DEVICE_ID")

# Enable logging to see underlying requests if needed
logging.basicConfig(level=logging.WARN)


def check_device():
    print(f"\n--- Diagnostic: Checking Device Status via HTTP API ---")
    print(f"Endpoint: {ENDPOINT}")
    print(f"Device ID: {DEVICE_ID}")

    if not all([ACCESS_ID, ACCESS_SECRET, ENDPOINT, DEVICE_ID]):
        print("Missing .env variables.")
        return

    openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_SECRET)

    if not openapi.is_connect():
        print("Cloud Connection Failed. Credentials still wrong?")
        return

    print("Cloud Connection OK.")
    print("Querying device details...\n")

    # 1. Get Device Details
    # /v1.0/devices/{device_id}
    response = openapi.get(f"/v1.0/devices/{DEVICE_ID}")

    if response.get("success"):
        print("Device Found & Linked!")
        result = response.get("result", {})
        print(f"   Name: {result.get('name')}")
        print(f"   Online: {result.get('online')}")
        print(f"   Product Name: {result.get('product_name')}")
        print(f"   Status: {json.dumps(result.get('status'), indent=2)}")

        if not result.get("online"):
            print("\nWARNING: Device is reported as OFFLINE. It won't send events.")
    else:
        print("Failed to get device details.")
        print(f"   Error Code: {response.get('code')}")
        print(f"   Error Msg: {response.get('msg')}")
        print("\nPossible Causes:")
        print(
            "1. Device is NOT added to this Project (Tuya Console > Cloud > Development > Linked Devices)."
        )
        print("2. Device is in a different Data Center region than the Project.")
        print("3. Device ID is incorrect.")


if __name__ == "__main__":
    check_device()
