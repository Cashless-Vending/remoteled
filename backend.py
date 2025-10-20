from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import random
import asyncio
import json
from bleak import BleakClient, BleakScanner

app = FastAPI()

# BLE Configuration (from Pi deep link: remoteled://connect/2C:CF:67:7C:DF:AB/ED5C/5B57/6372)
SERVICE_UUID = "0000EC4E-0000-1000-8000-00805f9b34fb"
CHAR_UUID = "00004679-0000-1000-8000-00805f9b34fb"
BLE_KEY = "B2AF"
PI_ADDRESS = "2C:CF:67:7C:DF:AB"  # Direct address from deep link

async def find_pi_device():
    """Scan for Pi by checking which device has our SERVICE_UUID"""
    print(f"[BLE] Scanning for device with service UUID: {SERVICE_UUID}")
    devices = await BleakScanner.discover(timeout=10.0, return_adv=True)

    print(f"[BLE] Found {len(devices)} devices, checking for our service...")

    # Try connecting to each device to check if it has our service
    for address, (device, adv_data) in devices.items():
        # Check if our service UUID is advertised
        if SERVICE_UUID.lower() in [str(uuid).lower() for uuid in adv_data.service_uuids]:
            print(f"[BLE] ✓ Found Pi at {address} (advertised service matches)")
            return address

    # Fallback: try devices with no name (Pi might be one of them)
    print(f"[BLE] Service not advertised, trying unnamed devices...")
    for address, (device, adv_data) in devices.items():
        if device.name is None or device.name == "":
            print(f"[BLE] Trying unnamed device: {address}")
            try:
                async with BleakClient(address, timeout=5.0) as client:
                    services = await client.get_services()
                    for service in services:
                        if service.uuid.lower() == SERVICE_UUID.lower():
                            print(f"[BLE] ✓ Found Pi at {address} (service discovered after connect)")
                            return address
            except Exception as e:
                continue

    print(f"[BLE] Pi not found in scan results")
    return None

async def trigger_led(color: str, duration: int):
    """Send BLE command to Pi to trigger LED"""
    print(f"\n{'='*50}")
    print(f"[BLE] Triggering {color} LED for {duration}s")
    print(f"{'='*50}")

    try:
        # Scan for device
        print("[BLE] Scanning for Pi...")
        device_address = await find_pi_device()
        if not device_address:
            print("[BLE] ERROR: Pi not found!")
            return

        print(f"[BLE] Found Pi at {device_address}")

        # Turn LED ON
        print(f"[BLE] Connecting to turn {color} LED ON...")
        async with BleakClient(device_address, timeout=10.0) as client:
            payload = {
                "command": "ON",
                "color": color.lower(),
                "bleKey": BLE_KEY
            }
            await client.write_gatt_char(CHAR_UUID, json.dumps(payload).encode('utf-8'))
            print(f"[BLE] ✓ {color} LED turned ON")

        # Wait
        await asyncio.sleep(duration)

        # Turn LED OFF
        print(f"[BLE] Connecting to turn {color} LED OFF...")
        async with BleakClient(device_address, timeout=10.0) as client:
            payload = {
                "command": "OFF",
                "color": color.lower(),
                "bleKey": BLE_KEY
            }
            await client.write_gatt_char(CHAR_UUID, json.dumps(payload).encode('utf-8'))
            print(f"[BLE] ✓ {color} LED turned OFF")

    except Exception as e:
        print(f"[BLE] ERROR: {e}")
        import traceback
        traceback.print_exc()

class PaymentRequest(BaseModel):
    amount: float
    service: str = "basic"

class PaymentResponse(BaseModel):
    status: str  # "success", "fail", "processing"
    led_color: str  # "green", "red", "yellow"
    duration: int  # seconds
    message: str

@app.post("/payment", response_model=PaymentResponse)
async def process_payment(payment: PaymentRequest, background_tasks: BackgroundTasks):
    """
    Fake payment endpoint for testing.
    Returns random status and automatically triggers Pi LED via BLE.

    Status → LED mapping:
    - success → green LED
    - fail → red LED
    - processing → yellow LED
    """

    # Fake payment logic - randomly assign status
    statuses = ["success", "fail", "processing"]
    weights = [0.7, 0.2, 0.1]  # 70% success, 20% fail, 10% processing
    status = random.choices(statuses, weights=weights)[0]

    # Map status to LED color
    led_mapping = {
        "success": "green",
        "fail": "red",
        "processing": "yellow"
    }

    led_color = led_mapping[status]

    # Duration: 15 seconds for demo
    duration = 15

    # Trigger LED in background (non-blocking)
    print(f"[API] Payment {status} - triggering {led_color} LED")
    background_tasks.add_task(trigger_led, led_color, duration)

    return PaymentResponse(
        status=status,
        led_color=led_color,
        duration=duration,
        message=f"Payment {status} - Amount: ${payment.amount}"
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}
