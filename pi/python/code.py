import json
import random
import threading
import time
from bluezero import adapter, peripheral
from led_service import LEDService

# Initialize LED service
led_service = LEDService()

# Global state for the LED and BLE characteristics
led_state = 'off'
trigger = threading.Event()
SERVICE_UUID = None
CHAR_UUID = None
SHORT_SERVICE_UUID = None
SHORT_CHAR_UUID = None
bleKey = None
current_peripheral = None  # Reference to track the current peripheral object
led_peripheral = None
WEB_MESSAGE = "Loading Bluetooth..."
QR_DATA_FILE = '/var/www/html/qr_data.json'


# Helper function to generate new random UUIDs
def generate_new_uuids(just_char=True):
    global SHORT_SERVICE_UUID, SHORT_CHAR_UUID, SERVICE_UUID, CHAR_UUID, bleKey
    if not just_char:
        print("Generating Service UUID")
        SHORT_SERVICE_UUID = '{:04X}'.format(random.randint(0x0001, 0xFFFF))
        SERVICE_UUID = '0000'+SHORT_SERVICE_UUID+'-0000-1000-8000-00805f9b34fb'
    SHORT_CHAR_UUID = '{:04X}'.format(random.randint(0x0001, 0xFFFF))
    CHAR_UUID = '0000'+SHORT_CHAR_UUID+'-0000-1000-8000-00805f9b34fb'
    bleKey = '{:04X}'.format(random.randint(0x0001, 0xFFFF))
    print(f"New Service UUID: {SERVICE_UUID}, Characteristic UUID: {CHAR_UUID}")


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

            if request_key == bleKey:
                if command == "ON":
                    # Use LED service to turn on requested LED (turns off others first)
                    if led_service.set_color_exclusive(color):
                        led_state = f'{color}_on'
                    else:
                        print(f"Unknown color: {color}")

                elif command == "OFF":
                    # Use LED service to turn off all LEDs
                    led_service.turn_off_all()
                    led_state = 'off'

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

def generate_deep_link(adapter_address, service_uuid, char_uuid, bleKey, device_id=None):
    # Create a deep link URL including device_id if provided
    global WEB_MESSAGE
    if device_id:
        deep_link = f"remoteled://connect/{adapter_address}/{service_uuid}/{char_uuid}/{bleKey}?deviceId={device_id}"
    else:
        deep_link = f"remoteled://connect/{adapter_address}/{service_uuid}/{char_uuid}/{bleKey}"
    WEB_MESSAGE = deep_link
    print(f"Generated Deep Link: {deep_link}")
    publish_qr_code(deep_link)


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

    # Generate initial UUIDs for the service and characteristic
    generate_new_uuids(False)

    # Setup the initial Bluezero Peripheral
    current_peripheral = setup_peripheral(adapter_address,False)

    # Generate and publish the deep link for QR code
    generate_deep_link(adapter_address, SHORT_SERVICE_UUID, SHORT_CHAR_UUID, bleKey, device_id)

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
