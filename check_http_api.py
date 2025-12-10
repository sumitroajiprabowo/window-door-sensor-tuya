from tuya_connector import TuyaOpenAPI
import os
import logging
from dotenv import load_dotenv

load_dotenv()

ACCESS_ID = os.getenv("TUYA_ACCESS_ID")
ACCESS_SECRET = os.getenv("TUYA_ACCESS_SECRET")

# List of HTTP Endpoints
ENDPOINTS = {
    "China Data Center": "https://openapi.tuyacn.com",
    "Western America Data Center": "https://openapi.tuyaus.com",
    "Eastern America Data Center": "https://openapi-ueaz.tuyaus.com",
    "Central Europe Data Center": "https://openapi.tuyaeu.com",
    "Western Europe Data Center": "https://openapi-weaz.tuyaeu.com",
    "India Data Center": "https://openapi.tuyain.com",
    "Singapore Data Center": "https://openapi-sg.iotbing.com",
}

logging.basicConfig(level=logging.CRITICAL)  # Silence internal logs


def check_all_regions():
    print(f"--- Diagnostic: Testing Tuya HTTP API across all regions ---")
    print(f"Access ID: {ACCESS_ID}")

    if not ACCESS_ID or not ACCESS_SECRET:
        print("Credentials missing in .env")
        return

    success_region = None

    for name, url in ENDPOINTS.items():
        print(f"Testing {name} ({url})... ", end="")
        try:
            openapi = TuyaOpenAPI(url, ACCESS_ID, ACCESS_SECRET)
            if openapi.is_connect():
                print("CONNECTED!")
                success_region = (name, url)
                break
            else:
                print("Failed")
        except Exception as e:
            print(f"Error: {e}")

    if success_region:
        print(f"\nSUCCESS! Your project is located in: {success_region[0]}")
        print(f"Please update your .env file:")
        print(f"TUYA_ENDPOINT={success_region[1]}")
        print(
            f"TUYA_PULSAR_ENDPOINT= (Set the matching pulsar endpoint for {success_region[0]})"
        )
    else:
        print("\nFailed to connect to any region.")
        print("   -> DEFINITE CAUSE: Your Access ID or Access Secret is INVALID.")
        print("      Please check the Tuya IoT Console and copy them again.")


if __name__ == "__main__":
    check_all_regions()
