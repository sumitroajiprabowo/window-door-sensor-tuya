#!/usr/bin/env python3
"""
Test WhatsApp API - Verify WhatsApp message sending works
"""
import os
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

print("\n" + "=" * 70)
print("WHATSAPP API TEST")
print("=" * 70)

# Import after load_dotenv
from config.Config import WhatsAppConfig
from services.whatsapp_service import (
    send_whatsapp_message,
    send_door_opened_alert,
    send_door_closed_alert,
)

print(f"API URL: {WhatsAppConfig.API_URL}")
print(f"Username: {WhatsAppConfig.API_USER}")
print(
    f"Password: {'*' * len(WhatsAppConfig.API_PASSWORD) if WhatsAppConfig.API_PASSWORD else 'NOT SET'}"
)
print(f"Group ID: {WhatsAppConfig.GROUP_ID}")
print("=" * 70)

if not WhatsAppConfig.API_PASSWORD:
    print("\nERROR: WA_API_PASSWORD not set in .env file!")
    print("   Please add: WA_API_PASSWORD=your_password")
    sys.exit(1)

print("\nTest 1: Sending test message...")
result = send_whatsapp_message("TEST: WhatsApp API Connection")

if result:
    print("Test 1 PASSED: Message sent successfully!\n")
else:
    print("Test 1 FAILED: Could not send message\n")
    sys.exit(1)

print("Test 2: Sending door opened alert...")
result = send_door_opened_alert()

if result:
    print("Test 2 PASSED: Door opened alert sent!\n")
else:
    print("Test 2 FAILED: Could not send door opened alert\n")
    sys.exit(1)

print("Test 3: Sending door closed alert...")
result = send_door_closed_alert()

if result:
    print("Test 3 PASSED: Door closed alert sent!\n")
else:
    print("Test 3 FAILED: Could not send door closed alert\n")
    sys.exit(1)

print("=" * 70)
print("ALL TESTS PASSED!")
print("=" * 70)
print("\nCheck your WhatsApp group to verify messages were received:")
print(f"   - TEST: WhatsApp API Connection")
print(f"   - PINTU SERVER DIBUKA")
print(f"   - PINTU SERVER DITUTUP")
print()
