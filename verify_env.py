import os

from dotenv import load_dotenv

load_dotenv()

KEYS = ["TUYA_ACCESS_ID", "TUYA_ACCESS_SECRET", "TUYA_ENDPOINT", "DEVICE_ID"]

print(f"--- Checking .env formatting ---")
for key in KEYS:
    val = os.getenv(key)
    if val is None:
        print(f"{key} is MISSING")
        continue

    # Obfuscate
    visible = val[:4] + "*" * (len(val) - 4) if len(val) > 4 else "****"

    issues = []
    if val.startswith(" ") or val.endswith(" "):
        issues.append("Has leading/trailing whitespace")
    if val.startswith("'") or val.startswith('"'):
        issues.append("Has quotes (dotenv might handle this, but checking)")

    if issues:
        print(f"{key}: {visible} -> Issues: {', '.join(issues)}")
    else:
        print(f"{key}: Valid format")
