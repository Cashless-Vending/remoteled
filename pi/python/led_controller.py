#!/usr/bin/env python3
"""
LED Controller - MQTT Subscriber for Payment Status
Subscribes to 'led/control' topic and controls 3 LEDs based on payment status
"""
import json
import time
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

# GPIO Pin Configuration (BCM numbering)
LED_PINS = {
    'led1': 17,  # GPIO 17 - LED 1
    'led2': 27,  # GPIO 27 - LED 2
    'led3': 22,  # GPIO 22 - LED 3
}

# LED Color Mapping
LED_COLORS = {
    'yellow': 'led1',  # Payment in progress
    'green': 'led2',   # Payment success
    'red': 'led3',     # Payment failed
}

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "led/control"

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for pin in LED_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

print(f"LED Controller started. GPIO pins initialized: {LED_PINS}")

def turn_off_all_leds():
    """Turn off all LEDs"""
    for pin in LED_PINS.values():
        GPIO.output(pin, GPIO.LOW)
    print("All LEDs turned OFF")

def control_led(led_name, state):
    """
    Control a specific LED
    Args:
        led_name: 'led1', 'led2', or 'led3'
        state: 'on', 'off', 'blink'
    """
    if led_name not in LED_PINS:
        print(f"Error: Unknown LED '{led_name}'")
        return

    pin = LED_PINS[led_name]

    if state == 'on':
        GPIO.output(pin, GPIO.HIGH)
        print(f"LED {led_name} (GPIO {pin}) turned ON")
    elif state == 'off':
        GPIO.output(pin, GPIO.LOW)
        print(f"LED {led_name} (GPIO {pin}) turned OFF")
    elif state == 'blink':
        print(f"LED {led_name} (GPIO {pin}) BLINKING (3 times)")
        for _ in range(3):
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.3)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(0.3)

def handle_payment_status(status, color=None, led=None, action='on'):
    """
    Handle payment status and control LEDs accordingly
    Args:
        status: 'processing', 'success', 'failed', or custom
        color: 'yellow', 'green', 'red' (optional, overrides status)
        led: 'led1', 'led2', 'led3' (optional, direct LED control)
        action: 'on', 'off', 'blink'
    """
    print(f"\n>>> Received: status={status}, color={color}, led={led}, action={action}")

    # Turn off all LEDs first
    turn_off_all_leds()

    # Determine which LED to control
    target_led = None

    if led:
        # Direct LED control
        target_led = led
    elif color:
        # Color-based control
        target_led = LED_COLORS.get(color)
    else:
        # Status-based control
        status_map = {
            'processing': 'led1',  # Yellow
            'success': 'led2',     # Green
            'failed': 'led3',      # Red
        }
        target_led = status_map.get(status)

    if target_led:
        control_led(target_led, action)
    else:
        print(f"Error: Could not determine LED for status={status}, color={color}, led={led}")

def on_connect(client, userdata, flags, reason_code, properties):
    """Callback when connected to MQTT broker"""
    if reason_code == 0:
        print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
        print("\nWaiting for LED control messages...")
        print("Expected JSON format:")
        print('  {"status": "processing|success|failed"}')
        print('  {"color": "yellow|green|red", "action": "on|off|blink"}')
        print('  {"led": "led1|led2|led3", "action": "on|off|blink"}\n')
    else:
        print(f"Failed to connect to MQTT broker. Reason code: {reason_code}")

def on_message(client, userdata, msg):
    """Callback when message received on subscribed topic"""
    try:
        payload = msg.payload.decode('utf-8')
        print(f"\n[MQTT] Topic: {msg.topic}, Payload: {payload}")

        # Parse JSON payload
        data = json.loads(payload)

        # Extract parameters
        status = data.get('status')
        color = data.get('color')
        led = data.get('led')
        action = data.get('action', 'on')

        # Handle LED control
        handle_payment_status(status, color, led, action)

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}")
    except Exception as e:
        print(f"Error processing message: {e}")

def on_disconnect(client, userdata, reason_code, properties):
    """Callback when disconnected from MQTT broker"""
    print(f"\nDisconnected from MQTT broker. Reason code: {reason_code}")
    turn_off_all_leds()

def main():
    """Main function"""
    # Create MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    # Connect to broker
    try:
        print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}...")
        client.connect(MQTT_BROKER, MQTT_PORT, 60)

        # Start MQTT loop
        client.loop_forever()

    except KeyboardInterrupt:
        print("\n\nShutting down LED controller...")
        turn_off_all_leds()
        client.disconnect()
        GPIO.cleanup()
        print("GPIO cleaned up. Goodbye!")
    except Exception as e:
        print(f"Error: {e}")
        turn_off_all_leds()
        GPIO.cleanup()

if __name__ == '__main__':
    main()
