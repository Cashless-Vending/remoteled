#!/usr/bin/env python3
"""
LED Service - Unified LED control for RemoteLED
Provides a single, consistent interface for controlling GPIO LEDs across all implementations.
"""
import time
import RPi.GPIO as GPIO


class LEDService:
    """
    Unified LED control service

    Usage:
        led_service = LEDService()
        led_service.set_led("green", "on")
        led_service.blink("yellow", times=3)
        led_service.turn_off_all()
    """

    # Canonical GPIO pin mapping (BCM numbering)
    # This is the single source of truth for all LED implementations
    PINS = {
        "green": 17,   # Success
        "yellow": 19,  # Processing
        "red": 27      # Failed
    }

    def __init__(self):
        """Initialize GPIO pins"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup all LED pins as outputs, initially LOW
        for color, pin in self.PINS.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        print(f"[LEDService] Initialized GPIO pins: {self.PINS}")

    def set_led(self, color: str, state: str) -> bool:
        """
        Control a specific LED

        Args:
            color: LED color ('green', 'yellow', 'red')
            state: 'on' or 'off'

        Returns:
            bool: True if successful, False if invalid color
        """
        color = color.lower()
        state = state.lower()

        if color not in self.PINS:
            print(f"[LEDService] ERROR: Unknown color '{color}'")
            return False

        pin = self.PINS[color]

        if state == "on":
            GPIO.output(pin, GPIO.HIGH)
            print(f"[LEDService] {color.upper()} LED (GPIO {pin}) turned ON")
        elif state == "off":
            GPIO.output(pin, GPIO.LOW)
            print(f"[LEDService] {color.upper()} LED (GPIO {pin}) turned OFF")
        else:
            print(f"[LEDService] ERROR: Unknown state '{state}'")
            return False

        return True

    def turn_off_all(self):
        """Turn off all LEDs"""
        for color, pin in self.PINS.items():
            GPIO.output(pin, GPIO.LOW)
        print("[LEDService] All LEDs turned OFF")

    def blink(self, color: str, times: int = 3, interval: float = 0.3):
        """
        Blink a specific LED

        Args:
            color: LED color ('green', 'yellow', 'red')
            times: Number of blinks (default: 3)
            interval: Time between blinks in seconds (default: 0.3)

        Returns:
            bool: True if successful, False if invalid color
        """
        color = color.lower()

        if color not in self.PINS:
            print(f"[LEDService] ERROR: Unknown color '{color}'")
            return False

        pin = self.PINS[color]
        print(f"[LEDService] {color.upper()} LED (GPIO {pin}) blinking {times} times")

        for _ in range(times):
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(interval)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(interval)

        return True

    def set_color_exclusive(self, color: str):
        """
        Turn on a specific LED and turn off all others

        Args:
            color: LED color to turn on ('green', 'yellow', 'red')

        Returns:
            bool: True if successful, False if invalid color
        """
        color = color.lower()

        if color not in self.PINS:
            print(f"[LEDService] ERROR: Unknown color '{color}'")
            return False

        # Turn off all LEDs first
        self.turn_off_all()

        # Turn on the requested LED
        pin = self.PINS[color]
        GPIO.output(pin, GPIO.HIGH)
        print(f"[LEDService] {color.upper()} LED (GPIO {pin}) turned ON (exclusive)")

        return True

    def cleanup(self):
        """Clean up GPIO resources"""
        self.turn_off_all()
        GPIO.cleanup()
        print("[LEDService] GPIO cleaned up")

    def get_pin(self, color: str) -> int:
        """
        Get the GPIO pin number for a color

        Args:
            color: LED color ('green', 'yellow', 'red')

        Returns:
            int: GPIO pin number, or None if invalid color
        """
        return self.PINS.get(color.lower())


# Example usage
if __name__ == "__main__":
    import sys

    led = LEDService()

    try:
        print("\nTesting LED Service...")
        print("=" * 50)

        # Test each color
        for color in ["green", "yellow", "red"]:
            print(f"\nTesting {color} LED:")
            led.set_color_exclusive(color)
            time.sleep(1)

        # Test blinking
        print("\nTesting blink:")
        led.turn_off_all()
        led.blink("yellow", times=3)

        # Turn off all
        print("\nTurning off all LEDs")
        led.turn_off_all()

        print("\n" + "=" * 50)
        print("LED Service test complete!")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        led.cleanup()
