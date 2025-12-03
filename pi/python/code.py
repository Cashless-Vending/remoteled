import json
import os
import threading
import time
from bluezero import adapter, peripheral
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LED service will be initialized lazily in main()
led_service = None

# Hardcoded BLE UUIDs (fixed for all machines)
SHORT_SERVICE_UUID = '7514'
SHORT_CHAR_UUID = 'DE40'
BLE_KEY = '9F64'

# Full UUIDs
SERVICE_UUID = f'0000{SHORT_SERVICE_UUID}-0000-1000-8000-00805f9b34fb'
CHAR_UUID = f'0000{SHORT_CHAR_UUID}-0000-1000-8000-00805f9b34fb'

# Machine configuration
MACHINE_ID = os.getenv('MACHINE_ID', 'UNKNOWN')
DEVICE_ID = os.getenv('DEVICE_ID', 'd1111111-1111-1111-1111-111111111111')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://192.168.1.158:9999')

# Global state for the LED and BLE characteristics
led_state = 'off'
trigger = threading.Event()
current_peripheral = None
led_peripheral = None
WEB_MESSAGE = "Loading Bluetooth..."
STATE_FILE = os.getenv('KIOSK_STATE_FILE', '/var/www/html/state.json')
QR_DATA_FILE = '/var/www/html/qr_data.json'  # Legacy file used by old static kiosk
DETAIL_URL = None  # Store detail URL to show QR code again after service ends


def _write_json_atomic(path, data):
    """Write JSON to a file atomically and ensure world-readable permissions."""
    try:
        target_dir = os.path.dirname(path)
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)

        temp_file = path + '.tmp'
        with open(temp_file, 'w') as f:
            json.dump(data, f)
        os.replace(temp_file, path)
        os.chmod(path, 0o666)
    except PermissionError as e:
        print(f"[STATE] ❌ Permission denied writing to {path}: {e}")
    except Exception as e:
        print(f"[STATE] ❌ Error writing {path}: {e}")


def update_kiosk_state(status, qr_url=None, message=None, duration_seconds=None, started_at=None, extra=None):
    """Publish kiosk state.json so the React kiosk can render the correct view."""
    payload = {
        'status': status,
        'timestamp': int(time.time() * 1000)
    }

    if qr_url:
        payload['qr_url'] = qr_url
    if message:
        payload['message'] = message
    if duration_seconds is not None:
        payload['duration_seconds'] = duration_seconds
    if started_at is not None:
        payload['started_at'] = started_at
    if extra:
        payload.update(extra)

    _write_json_atomic(STATE_FILE, payload)


def publish_qr_code(deep_link):
    """Write QR data to both legacy kiosk file and new React kiosk state.json."""
    global WEB_MESSAGE
    WEB_MESSAGE = deep_link
    data = {'message': deep_link, 'timestamp': int(time.time() * 1000)}

    # Legacy support for the old static kiosk
    _write_json_atomic(QR_DATA_FILE, data)

    # New React kiosk state
    update_kiosk_state(status='QR', qr_url=deep_link, message='Scan QR Code')

    display_link = deep_link[:60] + "..." if len(deep_link) > 60 else deep_link
    print(f"[QR] ✅ Published: {display_link}")


def init_led_service():
    """Initialize LED service with error handling"""
    global led_service
    try:
        from led_service import LEDService
        led_service = LEDService()
        print("[LED] ✅ LEDService initialized successfully")
        return True
    except Exception as e:
        print(f"[LED] ⚠️  LEDService initialization failed: {e}")
        print("[LED] ⚠️  LED control will be disabled")
        # Create a mock LED service that does nothing
        led_service = MockLEDService()
        return False


class MockLEDService:
    """Mock LED service for when GPIO is not available"""
    def set_led(self, color, state):
        print(f"[MockLED] set_led({color}, {state})")
        return True
    
    def turn_off_all(self):
        print("[MockLED] turn_off_all()")
    
    def blink(self, color, times=3, interval=0.3):
        print(f"[MockLED] blink({color}, times={times})")
        return True
    
    def set_color_exclusive(self, color):
        print(f"[MockLED] set_color_exclusive({color})")
        return True
    
    def is_blinking(self):
        return False
    
    def stop_blink(self):
        pass


class LEDController:
    tx_obj = None

    @classmethod
    def on_connect(cls, ble_device):
        print(f"[BLE] ✅ Device connected: {ble_device}")
        # Inform kiosk that device is connected - stay on this until service ends
        update_kiosk_state(status='CONNECTED', qr_url=DETAIL_URL, message='Device Connected')

    @classmethod
    def on_disconnect(cls, adapter_address, device_address):
        print(f"[BLE] Device disconnected: {device_address}")
        # Don't restore QR code here - wait for OFF command from app
        # The app will send OFF command when service is complete
        # This keeps the kiosk showing "CONNECTED" during service
        print("[BLE] BLE disconnected (kiosk stays on current screen until OFF command)")

    @classmethod
    def on_read(cls, options):
        print(f"[BLE] Read request - current state: {led_state}")
        return led_state.encode()

    @classmethod
    def on_write(cls, value, options):
        global led_state, led_service
        try:
            value_str = value.decode("utf-8")
            data = json.loads(value_str)
            command = data.get("command", "").upper()
            color = data.get("color", "green").lower()
            request_key = data.get("bleKey", "")

            print(f"\n[BLE] ▶ Received: {command} color={color}")
            
            # Log if a blink is currently running
            if led_service and led_service.is_blinking():
                print(f"[BLE] ⚠️  Interrupting ongoing blink...")

            if request_key != BLE_KEY:
                print(f"[BLE] ❌ Invalid BLE key")
                return

            if command == "ON":
                # Solid ON - device is running
                if led_service.set_color_exclusive(color):
                    led_state = f'{color}_on'
                    print(f"[LED] ✅ {color.upper()} SOLID ON")
                    update_kiosk_state(
                        status='RUNNING',
                        qr_url=DETAIL_URL,
                        message='Service Active',
                        duration_seconds=data.get("duration_seconds") or data.get("duration"),
                        started_at=data.get("started_at") or int(time.time() * 1000)
                    )
                else:
                    print(f"[LED] ❌ Unknown color: {color}")

            elif command == "BLINK":
                # Blink mode - payment processing (non-blocking)
                times = data.get("times", 5)
                interval = data.get("interval", 0.5)
                if led_service.blink(color, times=times, interval=interval):
                    led_state = f'{color}_blinking'
                    print(f"[LED] ✅ {color.upper()} BLINKING ({times}x)")
                    update_kiosk_state(status='SCANNED', qr_url=DETAIL_URL, message='Processing...')
                else:
                    print(f"[LED] ❌ Unknown color: {color}")

            elif command == "OFF":
                # Turn off all LEDs and set back to RED (idle state)
                led_service.turn_off_all()
                time.sleep(0.1)  # Brief pause before setting RED
                led_service.set_color_exclusive("red")
                led_state = 'red_idle'
                print(f"[LED] ✅ Service ended → RED (idle)")

                # Restore QR code for next user
                if DETAIL_URL:
                    publish_qr_code(DETAIL_URL)
                    print("[Status] QR code restored for next user")

            elif command == "CONNECT":
                print("[BLE] ✅ CONNECT command received")
                update_kiosk_state(status='CONNECTED', qr_url=DETAIL_URL, message='Device Connected')
            else:
                print(f"[BLE] ❓ Unknown command: {command}")

            # Update BLE characteristic value
            if cls.tx_obj:
                cls.tx_obj.set_value(value)

        except (json.JSONDecodeError, ValueError) as e:
            print(f"[BLE] ❌ Error parsing command: {e}")

    @classmethod
    def on_notify(cls, notifying, characteristic):
        if notifying:
            cls.tx_obj = characteristic
        else:
            cls.tx_obj = None

    @classmethod
    def update_tx(cls, value):
        if cls.tx_obj:
            cls.tx_obj.set_value(value)


def generate_deep_link(adapter_address, service_uuid, char_uuid, ble_key, device_id=None):
    """Generate cloud API URL for QR code"""
    global WEB_MESSAGE, DETAIL_URL

    detail_url = f"{API_BASE_URL}/detail?machineId={device_id or MACHINE_ID}&mac={adapter_address}&service={service_uuid}&char={char_uuid}&key={ble_key}"

    WEB_MESSAGE = detail_url
    DETAIL_URL = detail_url
    print(f"\n[QR] ✅ Generated Detail URL:")
    print(f"     {detail_url}")
    publish_qr_code(detail_url)


def setup_peripheral(adapter_address, just_char=True):
    """Setup the BLE peripheral"""
    print(f"[BLE] Setting up peripheral with adapter: {adapter_address}")
    global led_peripheral
    
    if not just_char:
        print("[BLE] Initializing adapter...")
        led_peripheral = peripheral.Peripheral(adapter_address, local_name='Remote LED')
        led_peripheral.add_service(srv_id=1, uuid=SERVICE_UUID, primary=True)
    
    led_peripheral.add_characteristic(
        srv_id=1,
        chr_id=1,
        uuid=CHAR_UUID,
        value=[],
        notifying=False,
        flags=['read', 'write'],
        read_callback=LEDController.on_read,
        write_callback=LEDController.on_write,
        notify_callback=LEDController.on_notify
    )

    if not just_char:
        led_peripheral.on_connect = LEDController.on_connect
        led_peripheral.on_disconnect = LEDController.on_disconnect

    return led_peripheral


def run_ble_peripheral(current_peripheral):
    """Run the BLE mainloop in a separate thread"""
    try:
        current_peripheral.publish()
    except Exception as e:
        print(f"[BLE] ❌ Error in peripheral: {e}")


def main(adapter_address, device_id=None):
    global current_peripheral

    print("\n" + "=" * 60)
    print("RemoteLED BLE Peripheral Starting")
    print("=" * 60)

    # Step 1: Clear stale QR data immediately
    print("\n[1/5] Clearing stale QR data...")
    publish_qr_code("Initializing...")

    # Step 2: Initialize LED service (with error handling)
    print("\n[2/5] Initializing LED service...")
    init_led_service()
    
    # Set initial LED state: RED (idle/ready)
    if led_service:
        led_service.set_color_exclusive("red")
        print("[LED] 🔴 Initial state: RED (ready/idle)")

    # Step 3: Get device ID
    print("\n[3/5] Loading configuration...")
    if device_id is None:
        device_id = os.getenv("DEVICE_ID")
    
    print(f"[BLE Config] Service UUID: {SERVICE_UUID}")
    print(f"[BLE Config] Char UUID: {CHAR_UUID}")
    print(f"[BLE Config] BLE Key: {BLE_KEY}")
    print(f"[Machine Config] Machine ID: {MACHINE_ID}")
    print(f"[Machine Config] Device ID: {device_id}")
    print(f"[Machine Config] API Base URL: {API_BASE_URL}")

    # Step 4: Setup BLE peripheral
    print("\n[4/5] Setting up BLE peripheral...")
    current_peripheral = setup_peripheral(adapter_address, False)

    # Step 5: Generate QR code URL BEFORE starting BLE
    print("\n[5/5] Generating QR code...")
    generate_deep_link(adapter_address, SHORT_SERVICE_UUID, SHORT_CHAR_UUID, BLE_KEY, device_id)

    # Start BLE in background thread
    print("\n" + "=" * 60)
    print("[BLE] Starting BLE peripheral...")
    ble_thread = threading.Thread(target=run_ble_peripheral, args=(current_peripheral,))
    ble_thread.start()
    print(f"[BLE] ✅ Peripheral published")
    print(f"[BLE] Service UUID: {SERVICE_UUID}")
    print("=" * 60)
    print("\n🟢 Ready! Waiting for connections...")
    print("   Press Ctrl+C to stop\n")

    # Keep running until interrupted
    try:
        while not trigger.is_set():
            time.sleep(0.1)
        current_peripheral.mainloop.quit()
    except KeyboardInterrupt:
        print("\n[BLE] Shutting down...")
        if led_service:
            led_service.turn_off_all()


if __name__ == '__main__':
    main(list(adapter.Adapter.available())[0].address)
