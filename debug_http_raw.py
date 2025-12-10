import hashlib
import hmac
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_ID = os.getenv("TUYA_ACCESS_ID")
ACCESS_SECRET = os.getenv("TUYA_ACCESS_SECRET")
ENDPOINT = "https://openapi-sg.iotbing.com"  # Singapore


def get_timestamp():
    return str(int(time.time() * 1000))


def calc_sign(client_id, secret, t):
    message = client_id + t
    sign = (
        hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256)
        .hexdigest()
        .upper()
    )
    return sign


def debug_http_token():
    if not ACCESS_ID or not ACCESS_SECRET:
        print("Credentials missing.")
        return

    t = get_timestamp()
    sign = calc_sign(ACCESS_ID, ACCESS_SECRET, t)

    headers = {
        "client_id": ACCESS_ID,
        "sign": sign,
        "t": t,
        "sign_method": "HMAC-SHA256",
    }

    url = f"{ENDPOINT}/v1.0/token?grant_type=1"

    print(f"--- Raw HTTP Debug ---")
    print(f"URL: {url}")
    print(f"Headers: {headers}")

    try:
        response = requests.get(url, headers=headers)
        print(f"\nResponse Code: {response.status_code}")
        print(f"Response Body: {response.text}")

    except Exception as e:
        print(f"Exception: {e}")


if __name__ == "__main__":
    debug_http_token()
