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


async def trigger_led_blink(color: str, times: int = 5, interval: float = 0.5):
    """
    Send BLE command to Pi to BLINK LED (for processing state)

    Args:
        color: LED color (green, red, yellow)
        times: Number of blinks
        interval: Time between blinks in seconds

    Returns:
        bool: True if successful, False otherwise
    """
    global _cached_pi_address

    print(f"\n{'='*60}")
    print(f"[BLE] ⚡ BLINKING LED: color={color.upper()}, times={times}, interval={interval}s")
    print(f"{'='*60}")

    try:
        # Try to find device (uses cache if available)
        print("[BLE] 🔍 Looking for Pi device...")
        device_address = await find_pi_device()
        if not device_address:
            print("[BLE] ❌ Pi not found!")
            return False

        print(f"[BLE] ✓ Found Pi at {device_address}")
        print(f"[BLE] 🔌 Connecting to Pi...")

        async with BleakClient(device_address, timeout=10.0) as client:
            # Send BLINK command
            payload = {
                "command": "BLINK",
                "color": color.lower(),
                "times": times,
                "interval": interval,
                "bleKey": settings.BLE_KEY
            }
            print(f"[BLE] 📤 Sending BLINK command: {payload}")
            await client.write_gatt_char(settings.BLE_CHAR_UUID, json.dumps(payload).encode('utf-8'))
            print(f"[BLE] ✅ {color.upper()} LED BLINKING (processing)")
            return True

    except Exception as e:
        print(f"[BLE] ❌ ERROR: {e}")
        if _cached_pi_address:
            _cached_pi_address = None
        return False


async def trigger_led_on(color: str):
    """
    Send BLE command to Pi to turn LED ON solid (for running state)

    Args:
        color: LED color (green, red, yellow)

    Returns:
        bool: True if successful, False otherwise
    """
    global _cached_pi_address

    print(f"\n{'='*60}")
    print(f"[BLE] 💡 LED SOLID ON: color={color.upper()}")
    print(f"{'='*60}")

    try:
        print("[BLE] 🔍 Looking for Pi device...")
        device_address = await find_pi_device()
        if not device_address:
            print("[BLE] ❌ Pi not found!")
            return False

        print(f"[BLE] ✓ Found Pi at {device_address}")
        print(f"[BLE] 🔌 Connecting to Pi...")

        async with BleakClient(device_address, timeout=10.0) as client:
            # Send ON command
            payload = {
                "command": "ON",
                "color": color.lower(),
                "bleKey": settings.BLE_KEY
            }
            print(f"[BLE] 📤 Sending ON command: {payload}")
            await client.write_gatt_char(settings.BLE_CHAR_UUID, json.dumps(payload).encode('utf-8'))
            print(f"[BLE] ✅ {color.upper()} LED SOLID ON (device running)")
            return True

    except Exception as e:
        print(f"[BLE] ❌ ERROR: {e}")
        if _cached_pi_address:
            _cached_pi_address = None
        return False


async def trigger_led_off():
    """
    Send BLE command to Pi to turn OFF all LEDs (for stopped state)

    Returns:
        bool: True if successful, False otherwise
    """
    global _cached_pi_address

    print(f"\n{'='*60}")
    print(f"[BLE] 🔴 LED OFF (device stopped)")
    print(f"{'='*60}")

    try:
        print("[BLE] 🔍 Looking for Pi device...")
        device_address = await find_pi_device()
        if not device_address:
            print("[BLE] ❌ Pi not found!")
            return False

        print(f"[BLE] ✓ Found Pi at {device_address}")
        print(f"[BLE] 🔌 Connecting to Pi...")

        async with BleakClient(device_address, timeout=10.0) as client:
            # Send OFF command
            payload = {
                "command": "OFF",
                "bleKey": settings.BLE_KEY
            }
            print(f"[BLE] 📤 Sending OFF command: {payload}")
            await client.write_gatt_char(settings.BLE_CHAR_UUID, json.dumps(payload).encode('utf-8'))
            print(f"[BLE] ✅ All LEDs turned OFF")
            return True

    except Exception as e:
        print(f"[BLE] ❌ ERROR: {e}")
        if _cached_pi_address:
            _cached_pi_address = None
        return False


# Legacy function for backward compatibility
async def trigger_led(color: str, duration: int):
    """
    Legacy LED trigger function (deprecated - use specific functions instead)
    """
    return await trigger_led_blink(color, times=5, interval=0.5)


def get_led_color_for_service_type(service_type: str) -> str:
    """
    Map service type to LED color

    Args:
        service_type: Service type (FIXED, VARIABLE, TRIGGER)

    Returns:
        str: LED color (green, yellow, red)
    """
    # Service Type to LED Color Mapping:
    # FIXED (e.g., Washer - fixed 40min cycle) -> GREEN
    # VARIABLE (e.g., Dryer - variable time) -> YELLOW
    # TRIGGER (e.g., Dispenser/Meter - instant) -> RED
    service_to_color = {
        "FIXED": "green",
        "VARIABLE": "yellow",
        "TRIGGER": "red"
    }
    return service_to_color.get(service_type.upper(), "green")


def get_led_color_for_status(status: str) -> str:
    """
    Map payment status to LED color (using unified config)

    Args:
        status: Payment status (success, fail, processing)

    Returns:
        str: LED color (green, red, yellow)
    """
    return settings.led_color_mapping.get(status.lower(), "green")
