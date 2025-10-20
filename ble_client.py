"""
BLE Client for Remote LED Control

HOW TO GET Pi's UUIDs:
1. Start your Pi with code.py running
2. Check Pi terminal output for:
   "New Service UUID: 0000XXXX-0000-1000-8000-00805f9b34fb"
   "Generated Deep Link: remoteled://connect/{address}/{service}/{char}/{bleKey}"
3. Use those values as arguments to this script

OR subscribe to MQTT topic "qr" to get the deep link
"""

import asyncio
import json
import sys
from bleak import BleakClient, BleakScanner

# Default UUID format from your Pi code
# You MUST update these with actual values from your Pi
SERVICE_UUID = "0000ED5C-0000-1000-8000-00805f9b34fb"
CHAR_UUID = "00005B57-0000-1000-8000-00805f9b34fb"
BLE_KEY = "6372"
DEVICE_NAME = "Remote LED"

async def find_device():
    """Scan for Pi BLE peripheral by name"""
    print(f"Scanning for device: {DEVICE_NAME}...")
    devices = await BleakScanner.discover(timeout=5.0)

    for device in devices:
        if device.name == DEVICE_NAME:
            print(f"Found device: {device.name} [{device.address}]")
            return device.address

    print(f"Device '{DEVICE_NAME}' not found!")
    return None

async def send_led_command(color: str, command: str = "ON"):
    """
    Send LED command to Pi via BLE

    Args:
        color: LED color (green, red, yellow)
        command: ON or OFF
    """

    # Find the Pi device
    device_address = await find_device()
    if not device_address:
        print("ERROR: Could not find Pi device. Is it running?")
        return False

    # Connect and send command
    try:
        async with BleakClient(device_address) as client:
            print(f"Connected to {device_address}")

            # Prepare command payload with color
            payload = {
                "command": command.upper(),
                "color": color.lower(),
                "bleKey": BLE_KEY
            }

            payload_bytes = json.dumps(payload).encode('utf-8')

            # Write to characteristic
            await client.write_gatt_char(CHAR_UUID, payload_bytes)
            print(f"Sent: {payload}")

            # Read response
            response = await client.read_gatt_char(CHAR_UUID)
            print(f"LED state: {response.decode()}")

            return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

async def trigger_payment_led(payment_status: str, duration: int = 10):
    """
    Trigger LED based on payment status

    Args:
        payment_status: "success", "fail", or "processing"
        duration: How long to keep LED on (seconds, default 10s)
    """

    # Map payment status to LED color
    led_mapping = {
        "success": "green",
        "fail": "red",
        "processing": "yellow"
    }

    color = led_mapping.get(payment_status, "green")

    print(f"\n{'='*50}")
    print(f"Payment Status: {payment_status}")
    print(f"LED Color: {color}")
    print(f"Duration: {duration}s")
    print(f"{'='*50}\n")

    # Find Pi device
    device_address = await find_device()
    if not device_address:
        print("ERROR: Could not find Pi device. Is it running?")
        return

    # Keep connection open for entire duration
    try:
        async with BleakClient(device_address, timeout=10.0) as client:
            # Turn LED ON
            payload_on = {
                "command": "ON",
                "color": color.lower(),
                "bleKey": BLE_KEY
            }
            await client.write_gatt_char(CHAR_UUID, json.dumps(payload_on).encode('utf-8'))
            print(f"✓ {color} LED turned ON")

            # Wait
            if duration > 0:
                print(f"Waiting {duration} seconds...")
                await asyncio.sleep(duration)

            # Turn LED OFF
            payload_off = {
                "command": "OFF",
                "color": color.lower(),
                "bleKey": BLE_KEY
            }
            await client.write_gatt_char(CHAR_UUID, json.dumps(payload_off).encode('utf-8'))
            print(f"✓ {color} LED turned OFF")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ble_client.py <payment_status> [duration]")
        print("  payment_status: success, fail, or processing")
        print("  duration: seconds (optional, default 10)")
        print("\nExample: python ble_client.py success 10")
        sys.exit(1)

    status = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    asyncio.run(trigger_payment_led(status, duration))
