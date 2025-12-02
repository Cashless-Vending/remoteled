import json
import os
import random
import threading
import time
from bluezero import adapter, peripheral
from led_service import LEDService
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize LED service
led_service = LEDService()

# Hardcoded BLE UUIDs (fixed for all machines)
SHORT_SERVICE_UUID = '7514'
SHORT_CHAR_UUID = 'DE40'
BLE_KEY = '9F64'

# Full UUIDs
SERVICE_UUID = f'0000{SHORT_SERVICE_UUID}-0000-1000-8000-00805f9b34fb'
CHAR_UUID = f'0000{SHORT_CHAR_UUID}-0000-1000-8000-00805f9b34fb'

# Machine configuration
MACHINE_ID = os.getenv('MACHINE_ID', 'UNKNOWN')
DEVICE_ID = os.getenv('DEVICE_ID', 'd1111111-1111-1111-1111-111111111111')  # Default to Laundry Room A test device
# Backend on Mac (update if host IP changes)
API_BASE_URL = os.getenv('API_BASE_URL', 'http://192.168.1.158:9999')

# Global state for the LED and BLE characteristics
led_state = 'off'
trigger = threading.Event()
current_peripheral = None  # Reference to track the current peripheral object
led_peripheral = None
WEB_MESSAGE = "Loading Bluetooth..."
QR_DATA_FILE = '/var/www/html/qr_data.json'

print(f"[BLE Config] Service UUID: {SERVICE_UUID}")
print(f"[BLE Config] Char UUID: {CHAR_UUID}")
print(f"[BLE Config] BLE Key: {BLE_KEY}")
print(f"[Machine Config] Machine ID: {MACHINE_ID}")
print(f"[Machine Config] Device ID: {DEVICE_ID}")
print(f"[Machine Config] API Base URL: {API_BASE_URL}")


# Write QR data to file for web page to read
def publish_qr_code(deep_link):
    global WEB_MESSAGE
    WEB_MESSAGE = deep_link
    data = {'message': deep_link, 'timestamp': int(time.time() * 1000)}
    try:
        with open(QR_DATA_FILE, 'w') as f:
            json.dump(data, f)
        print(f"Deep link written to file: {deep_link}")
    except Exception as e:
        print(f"Error writing QR data file: {e}")


class LEDController:
    tx_obj = None

    @classmethod
    def on_connect(cls, ble_device):
        global WEB_MESSAGE
        publish_qr_code("CONNECTED!")
        print("Connected to BLE device: ", ble_device)

    @classmethod
    def on_disconnect(cls, adapter_address, device_address):
        global current_peripheral
        print(f"Disconnected from BLE device: {device_address}")
        # Don't trigger exit - disconnects are normal after each request
        # trigger.set()

    @classmethod
    def on_read(cls, options):
        print(f"Current LED State: {led_state}")
        return led_state.encode()

    @classmethod
    def on_write(cls, value, options):
        global led_state
        try:
            value_str = value.decode("utf-8")
            data = json.loads(value_str)
            command = data.get("command", "").upper()
            color = data.get("color", "green").lower()
            request_key = data.get("bleKey", "")

            if request_key == BLE_KEY:
                if command == "ON":
                    # Solid ON - device is running
                    if led_service.set_color_exclusive(color):
                        led_state = f'{color}_on'
                        print(f"[LED] {color.upper()} SOLID ON (device running)")
                    else:
                        print(f"Unknown color: {color}")

                elif command == "BLINK":
                    # Blink mode - payment processing
                    times = data.get("times", 5)
                    interval = data.get("interval", 0.5)
                    if led_service.blink(color, times=times, interval=interval):
                        led_state = f'{color}_blinking'
                        print(f"[LED] {color.upper()} BLINKING (processing)")
                    else:
                        print(f"Unknown color: {color}")

                elif command == "OFF":
                    # Turn off all LEDs - device stopped
                    led_service.turn_off_all()
                    led_state = 'off'
                    print(f"[LED] ALL OFF (device stopped)")

                elif command == "CONNECT":
                    print("New Device Connected")
                    publish_qr_code("CONNECTED!")
                else:
                    print("Unknown command received")

            # Update BLE characteristic value
            if cls.tx_obj:
                cls.tx_obj.set_value(value)

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error processing write request: {e}")

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
    """
    Generate cloud API URL for QR code.
    The URL points to the FastAPI backend's /detail endpoint which will handle the payment/product details.
    User scans QR -> Android app opens URL via deep link -> Extracts BLE params -> Connects to device
    """
    global WEB_MESSAGE

    # Build cloud API URL with all BLE connection parameters
    detail_url = f"{API_BASE_URL}/detail?machineId={device_id or MACHINE_ID}&mac={adapter_address}&service={service_uuid}&char={char_uuid}&key={ble_key}"

    WEB_MESSAGE = detail_url
    print(f"Generated Detail URL: {detail_url}")
    publish_qr_code(detail_url)


def setup_peripheral(adapter_address, just_char=True):
    print("adapter_address:",adapter_address)
    global led_peripheral
    # Setup Bluezero Peripheral with the current UUIDs
    if not just_char:
        print("Initializing adapter")
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

    # Set BLE connection callbacks
    if not just_char:
        led_peripheral.on_connect = LEDController.on_connect
        led_peripheral.on_disconnect = LEDController.on_disconnect

    return led_peripheral

def run_ble_peripheral(current_peripheral):
    """Run the BLE mainloop in a separate thread."""
    try:
        current_peripheral.publish()
    except Exception as e:
        print(f"Error running BLE peripheral: {e}")

def main(adapter_address, device_id=None):
    global current_peripheral
    if device_id is None:
        device_id = os.getenv("DEVICE_ID")
    if device_id:
        print(f"[Pi] Using DEVICE_ID for deep link generation: {device_id}")
    else:
        print("[Pi] DEVICE_ID not provided; deep link will omit deviceId query parameter")

    # Setup the initial Bluezero Peripheral
    current_peripheral = setup_peripheral(adapter_address,False)

    # Generate and publish the cloud API URL for QR code
    generate_deep_link(adapter_address, SHORT_SERVICE_UUID, SHORT_CHAR_UUID, BLE_KEY, device_id)

    # Publish the BLE peripheral
    #current_peripheral.publish()
    ble_thread = threading.Thread(target=run_ble_peripheral, args=(current_peripheral,))
    ble_thread.start()
    print(f"BLE Peripheral published with Service UUID: {SERVICE_UUID}")

    # Keep the server running until the trigger event is set
    try:
        while not trigger.is_set():
            time.sleep(0.1)
        current_peripheral.mainloop.quit()    
    except KeyboardInterrupt:
        print("Stopping BLE Server")


if __name__ == '__main__':
    main(list(adapter.Adapter.available())[0].address)
