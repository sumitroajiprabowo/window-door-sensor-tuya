from tuya_connector import TuyaOpenAPI
import os
import logging
from dotenv import load_dotenv

load_dotenv()

ACCESS_ID = os.getenv("TUYA_ACCESS_ID")
ACCESS_SECRET = os.getenv("TUYA_ACCESS_SECRET")
ENDPOINT = "https://openapi-sg.iotbing.com"  # Singapore

# Enable verbose logging
logging.basicConfig(level=logging.DEBUG)


def check_sg_manual():
    print(f"--- Detailed Auth Debug for SG ---")
    print(f"Endpoint: {ENDPOINT}")
    print(f"Access ID: {ACCESS_ID}")

    try:
        openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_SECRET)
        print("Attempting to connect...")
        if openapi.is_connect():
            print("CONNECTED!")
        else:
            print("Connection Failed. Check logs above for 'msg' and 'code'.")

    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    check_sg_manual()
