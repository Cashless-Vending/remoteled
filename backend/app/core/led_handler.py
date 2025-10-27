"""
LED Handler - BLE communication for controlling Pi LEDs
"""
import asyncio
import json
from bleak import BleakClient, BleakScanner
from app.core.config import settings


# Cache Pi address after first successful connection
_cached_pi_address = None


async def find_pi_device(force_scan=False):
    """Scan for Pi by checking which device has our SERVICE_UUID"""
    global _cached_pi_address

    # Use cached address if available (unless force scan)
    if _cached_pi_address and not force_scan:
        print(f"[BLE] ✓ Using cached Pi address: {_cached_pi_address}")
        return _cached_pi_address

    print(f"[BLE] 🔍 Starting BLE scan for device with service UUID: {settings.BLE_SERVICE_UUID}")
    print(f"[BLE] 🔍 Scan timeout: 10 seconds...")
    devices = await BleakScanner.discover(timeout=10.0, return_adv=True)

    print(f"[BLE] 📡 Found {len(devices)} BLE devices total, checking for our service...")

    # Try connecting to each device to check if it has our service
    for address, (device, adv_data) in devices.items():
        # Check if our service UUID is advertised
        if settings.BLE_SERVICE_UUID.lower() in [str(uuid).lower() for uuid in adv_data.service_uuids]:
            print(f"[BLE] ✓ Found Pi at {address} (advertised service matches)")
            _cached_pi_address = address  # Cache it
            return address

    # Fallback: try devices with no name (Pi might be one of them)
    print(f"[BLE] ⚠️  Service not advertised, trying unnamed devices...")
    for address, (device, adv_data) in devices.items():
        if device.name is None or device.name == "":
            print(f"[BLE] 🔍 Trying unnamed device: {address}")
            try:
                async with BleakClient(address, timeout=5.0) as client:
                    services = await client.get_services()
                    for service in services:
                        if service.uuid.lower() == settings.BLE_SERVICE_UUID.lower():
                            print(f"[BLE] ✓ Found Pi at {address} (service discovered after connect)")
                            _cached_pi_address = address  # Cache it
                            return address
            except Exception as e:
                continue

    print(f"[BLE] ❌ Pi not found in scan results (no matching device)")
    return None


async def trigger_led(color: str, duration: int):
    """
    Send BLE command to Pi to trigger LED

    Args:
        color: LED color (green, red, yellow)
        duration: How long to keep LED on (seconds)

    Returns:
        bool: True if successful, False otherwise
    """
    global _cached_pi_address

    print(f"\n{'='*60}")
    print(f"[BLE] 💡 TRIGGERING LED: color={color.upper()}, duration={duration}s")
    print(f"{'='*60}")

    try:
        # Try to find device (uses cache if available)
        print("[BLE] 🔍 Step 1: Looking for Pi device via BLE scan...")
        device_address = await find_pi_device()
        if not device_address:
            print("[BLE] ❌ ERROR: Pi not found! (Expected if Pi is not powered on)")
            print("[BLE] 💡 This is normal for testing without hardware")
            return False

        print(f"[BLE] ✓ Step 2: Found Pi at {device_address}")

        # Keep connection open for entire duration (turn ON, wait, turn OFF)
        print(f"[BLE] 🔌 Step 3: Connecting to Pi...")
        async with BleakClient(device_address, timeout=10.0) as client:
            # Turn LED ON
            payload_on = {
                "command": "ON",
                "color": color.lower(),
                "bleKey": settings.BLE_KEY
            }
            print(f"[BLE] 📤 Step 4: Sending ON command: {payload_on}")
            await client.write_gatt_char(settings.BLE_CHAR_UUID, json.dumps(payload_on).encode('utf-8'))
            print(f"[BLE] ✅ {color.upper()} LED turned ON")

            # Wait while keeping connection open
            print(f"[BLE] ⏳ Step 5: Waiting {duration}s...")
            await asyncio.sleep(duration)

            # Turn LED OFF
            payload_off = {
                "command": "OFF",
                "color": color.lower(),
                "bleKey": settings.BLE_KEY
            }
            print(f"[BLE] 📤 Step 6: Sending OFF command: {payload_off}")
            await client.write_gatt_char(settings.BLE_CHAR_UUID, json.dumps(payload_off).encode('utf-8'))
            print(f"[BLE] ✅ {color.upper()} LED turned OFF")
            print(f"[BLE] 🎉 LED trigger completed successfully!")

            return True

    except Exception as e:
        print(f"[BLE] ❌ ERROR: {e}")
        print(f"[BLE] 💡 This is expected if Pi is not powered on or out of range")
        # If cached address failed, clear cache and retry once
        if _cached_pi_address:
            print("[BLE] 🔄 Cached address failed, clearing cache...")
            _cached_pi_address = None
        import traceback
        print("[BLE] 📋 Full error trace:")
        traceback.print_exc()
        return False


def get_led_color_for_status(status: str) -> str:
    """
    Map payment status to LED color (using unified config)

    Args:
        status: Payment status (success, fail, processing)

    Returns:
        str: LED color (green, red, yellow)
    """
    return settings.led_color_mapping.get(status.lower(), "green")
