from tuya_connector import TuyaOpenPulsar, TuyaCloudPulsarTopic
import websocket
import logging
import threading
import time
import sys

# Configure logging
logging.basicConfig(format="%(asctime)s %(levelname)s:%(message)s", level=logging.INFO)


class RegionTester:
    def __init__(self, access_id, access_secret):
        self.access_id = access_id
        self.access_secret = access_secret
        self.found_region = None
        self.stop_event = threading.Event()

    def test_region(self, name, endpoint):
        if self.stop_event.is_set():
            return

        print(f"\n--- Testing Region: {name} ({endpoint}) ---")

        # Capture error in closure
        status = {"error": None, "opened": False}

        def on_error(ws, error):
            status["error"] = error
            # print(f"   Error callback: {error}")

        def on_open(ws):
            status["opened"] = True
            print(f"   >>> SUCCESS! Connected to {name}")
            self.found_region = (name, endpoint)
            self.stop_event.set()
            ws.close()

        def on_close(ws, *args):
            pass

        # TuyaOpenPulsar creates a WebSocketApp internally but hides it.
        # We will manually create a WebSocketApp to have better control for testing.
        # But we need the auth generation logic from TuyaOpenPulsar.

        try:
            # We use TuyaOpenPulsar to generate the auth
            pulsar = TuyaOpenPulsar(
                self.access_id, self.access_secret, endpoint, TuyaCloudPulsarTopic.PROD
            )

            # Just set our handlers directly.
            # Based on source, TuyaOpenPulsar might essentially be a Thread that creates a WebSocketApp in run()
            # and passes self._on_open, self._on_message, self._on_error to it.
            # So setting these attributes on the instance SHOULD work.

            def custom_on_error(ws, error):
                if "401" in str(error) or "Unauthorized" in str(error):
                    status["error"] = "401 Unauthorized"
                else:
                    status["error"] = str(error)
                try:
                    ws.close()
                except:
                    pass

            def custom_on_open(ws):
                status["opened"] = True
                print(f"   SUCCESS! Connected to {name}")
                self.found_region = (name, endpoint)
                self.stop_event.set()
                try:
                    ws.close()
                except:
                    pass

            pulsar._on_error = custom_on_error
            pulsar._on_open = custom_on_open

            # Start in a separate thread so we can timeout
            t = threading.Thread(target=pulsar.start)
            t.daemon = True
            t.start()

            # Wait for result
            timeout = 5
            start_time = time.time()
            while time.time() - start_time < timeout:
                if status["opened"]:
                    break
                if status["error"]:
                    print(f"   Failed: {status['error']}")
                    break
                if self.stop_event.is_set():
                    break
                time.sleep(0.5)

            if not status["opened"] and not status["error"]:
                # If we timed out but no error, it might be hanging on connection or we missed the signal.
                # Assuming failure if not explicitly opened.
                print("   Timeout (Possible hang or auth silent fail).")

        except Exception as e:
            print(f"   Exception: {e}")


def main():
    import os
    from dotenv import load_dotenv

    load_dotenv()

    aid = os.getenv("TUYA_ACCESS_ID")
    sec = os.getenv("TUYA_ACCESS_SECRET")

    if not aid or not sec:
        print("Please set TUYA_ACCESS_ID and TUYA_ACCESS_SECRET in .env")
        return

    print(f"Testing credentials for ID: {aid}")

    # Common endpoints
    endpoints = [
        ("CN (China)", "wss://mqe.tuyacn.com:8285/"),
        ("US (Western America)", "wss://mqe.tuyaus.com:8285/"),
        ("EU (Central Europe)", "wss://mqe.tuyaeu.com:8285/"),
        ("IN (India)", "wss://mqe.tuyain.com:8285/"),
        ("WE (Western Europe)", "wss://mqe.tuyawe.com:8285/"),
        ("UE (Eastern America)", "wss://mqe.tuyaue.com:8285/"),
        ("SG (Singapore - IotBing)", "wss://mqe-sg.iotbing.com:8285/"),
    ]

    tester = RegionTester(aid, sec)

    for name, url in endpoints:
        if tester.stop_event.is_set():
            break
        tester.test_region(name, url)

    if tester.found_region:
        print(f"\nFOUND! Your project is in: {tester.found_region[0]}")
        print(f"Please update .env with:\nTUYA_PULSAR_ENDPOINT={tester.found_region[1]}")
    else:
        print("\nCould not connect to any region. Check your Access ID/Secret.")


if __name__ == "__main__":
    main()
