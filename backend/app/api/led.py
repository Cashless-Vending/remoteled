"""
LED Control API - Direct GPIO control for demo
In production, Android app will call these endpoints and relay to Pi via BLE
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal, Optional
import RPi.GPIO as GPIO

router = APIRouter(prefix="/led", tags=["led"])

# GPIO Pin Configuration (BCM numbering)
# Correct pins: 17, 27, 19
LED_PINS = {
    'led1': 17,  # GPIO 17 - Green (success)
    'led2': 27,  # GPIO 27 - Red (failed)
    'led3': 19,  # GPIO 19 - Yellow (processing)
}

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for pin in LED_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

print(f"✅ LED GPIO pins initialized: {LED_PINS}")


class LEDControlRequest(BaseModel):
    """LED control request model"""
    status: Optional[Literal["processing", "success", "failed"]] = None
    color: Optional[Literal["yellow", "green", "red"]] = None
    led: Optional[Literal["led1", "led2", "led3"]] = None
    action: Literal["on", "off", "blink"] = "on"


@router.post("/control")
def control_led(request: LEDControlRequest):
    """
    Control LED based on payment status

    Examples:
    - {"status": "processing"} → Yellow LED blinking
    - {"status": "success"} → Green LED on
    - {"status": "failed"} → Red LED on
    - {"color": "yellow", "action": "blink"} → Yellow LED blinks
    - {"led": "led1", "action": "off"} → LED1 off
    """
    # ALWAYS turn off all LEDs first
    for pin in LED_PINS.values():
        GPIO.output(pin, GPIO.LOW)

    # Determine which LED to control
    target_led = None

    if request.led:
        target_led = request.led
    elif request.color:
        color_map = {"yellow": "led3", "green": "led1", "red": "led2"}
        target_led = color_map.get(request.color)
    elif request.status:
        status_map = {"processing": "led3", "success": "led1", "failed": "led2"}
        target_led = status_map.get(request.status)

    if not target_led:
        raise HTTPException(status_code=400, detail="Must specify status, color, or led")

    pin = LED_PINS[target_led]

    # Auto-blink for processing status
    if request.status == "processing":
        request.action = "blink"

    # Execute action
    if request.action == "on":
        GPIO.output(pin, GPIO.HIGH)
        return {
            "success": True,
            "led": target_led,
            "pin": pin,
            "action": "on",
            "message": f"{target_led.upper()} (GPIO {pin}) turned ON"
        }
    elif request.action == "off":
        GPIO.output(pin, GPIO.LOW)
        return {
            "success": True,
            "led": target_led,
            "pin": pin,
            "action": "off",
            "message": f"{target_led.upper()} (GPIO {pin}) turned OFF"
        }
    elif request.action == "blink":
        import time
        for _ in range(3):
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(0.3)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(0.3)
        return {
            "success": True,
            "led": target_led,
            "pin": pin,
            "action": "blink",
            "message": f"{target_led.upper()} (GPIO {pin}) blinked 3 times"
        }


@router.get("/status")
def get_led_status():
    """Get current status of all LEDs"""
    status = {}
    for led_name, pin in LED_PINS.items():
        state = GPIO.input(pin)
        status[led_name] = {
            "pin": pin,
            "state": "ON" if state else "OFF"
        }
    return status


@router.post("/off")
def turn_off_all():
    """Turn off all LEDs"""
    for pin in LED_PINS.values():
        GPIO.output(pin, GPIO.LOW)
    return {
        "success": True,
        "message": "All LEDs turned OFF"
    }
