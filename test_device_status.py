#!/usr/bin/env python3
"""
Quick test of device status API
"""
from services.tuya_service import tuya_service
from config.Config import TuyaConfig
import json

print("\n" + "=" * 70)
print("TESTING DEVICE STATUS API")
print("=" * 70)
print(f"Device ID: {TuyaConfig.DEVICE_ID}")
print(f"API Endpoint: {TuyaConfig.API_ENDPOINT}")
print("=" * 70)

response = tuya_service.get_device_status(TuyaConfig.DEVICE_ID)

print("\nResponse:")
print(json.dumps(response, indent=2))

if response.get("success"):
    result = response.get("result", [])
    print("\nDevice Status:")
    for status in result:
        code = status.get("code")
        value = status.get("value")
        print(f"   {code}: {value}")

        if code == "doorcontact_state":
            state_text = "OPENED" if value else "CLOSED"
            print(f"\nDoor is {state_text}")
else:
    print(f"\nError: {response.get('msg')}")
