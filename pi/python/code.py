import json
import random
import threading
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
from bluezero import adapter, peripheral

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
GPIO.output(17, GPIO.LOW)  # Set initial state

# Global state for the LED and BLE characteristics
led_state = 'off'
mqtt_topic = "qr"
trigger = threading.Event()
SERVICE_UUID = None
CHAR_UUID = None
SHORT_SERVICE_UUID = None
SHORT_CHAR_UUID = None
bleKey = None
current_peripheral = None  # Reference to track the current peripheral object
led_peripheral = None
WEB_MESSAGE = "Loading Bluetooth..."


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


# MQTT client to publish QR code
def publish_qr_code(deep_link):
    client.publish(mqtt_topic, deep_link)
    print(f"Deep link published: {deep_link}")


class LEDController:
    tx_obj = None

    @classmethod
    def on_connect(cls, ble_device):
        global WEB_MESSAGE
        client.publish("qr","CONNECTED!")
        WEB_MESSAGE = "CONNECTED!"
        print("Connected to BLE device: ", ble_device)

    @classmethod
    def on_disconnect(cls, adapter_address, device_address):
        global current_peripheral
        print(f"Disconnected from BLE device: {device_address}")
        trigger.set()

    @classmethod
    def on_read(cls, options):
        print(f"Current LED State: {led_state}")
        return led_state.encode()

    @classmethod
    def on_write(cls, value, options):
        global led_state
        try:
            value_str = value.decode("utf-8")  # Decode bytes to string
            data = json.loads(value_str)  # Parse JSON data
            command = data.get("command", "").upper()
            request_key = data.get("bleKey", "")
            if request_key == bleKey:
                if command == "ON":
                    led_state = 'on'
                    GPIO.output(17, GPIO.HIGH)
                    print("GPIO pin 17 turned ON")
                elif command == "OFF":
                    led_state = 'off'
                    GPIO.output(17, GPIO.LOW)
                    print("GPIO pin 17 turned OFF")
                elif command == "CONNECT":
                    print("New Device Connected")
                    client.publish("qr","CONNECTED!")
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

def on_mqtt_message(client, userdata, msg):
    global WEB_MESSAGE
    publish_qr_code(WEB_MESSAGE)

def on_mqtt_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    client.subscribe("qr_backend")

def generate_deep_link(adapter_address, service_uuid, char_uuid, bleKey):
    # Create a deep link URL
    global WEB_MESSAGE
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

def main(adapter_address):
    global current_peripheral

    # Generate initial UUIDs for the service and characteristic
    generate_new_uuids(False)

    # Setup the initial Bluezero Peripheral
    current_peripheral = setup_peripheral(adapter_address,False)

    # Generate and publish the deep link for QR code
    generate_deep_link(adapter_address, SHORT_SERVICE_UUID, SHORT_CHAR_UUID, bleKey)

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


# MQTT Setup
broker_address = "localhost"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_mqtt_connect
client.on_message = on_mqtt_message
client.connect(broker_address)
client.loop_start()

if __name__ == '__main__':
    main(list(adapter.Adapter.available())[0].address)
