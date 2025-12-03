#!/usr/bin/env python3
"""
LED Service - Unified LED control for RemoteLED
Provides a single, consistent interface for controlling GPIO LEDs across all implementations.
"""
import time
import threading

# Try to import RPi.GPIO, fail gracefully if not available
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("[LEDService] WARNING: RPi.GPIO not available - running in mock mode")


class LEDService:
    """
    Unified LED control service with non-blocking blink support.

    Usage:
        led_service = LEDService()
        led_service.set_led("green", "on")
        led_service.blink("yellow", times=3)  # Non-blocking
        led_service.stop_blink()              # Stop any ongoing blink
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
        """Initialize GPIO pins and threading controls"""
        # Threading controls for non-blocking blink
        self._blink_thread = None
        self._stop_blink_flag = threading.Event()
        self._blink_lock = threading.Lock()
        self._gpio_available = GPIO_AVAILABLE

        if not GPIO_AVAILABLE:
            print("[LEDService] Running in mock mode (no GPIO)")
            return

        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

            # Setup all LED pins as outputs, initially LOW
            for color, pin in self.PINS.items():
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.LOW)

            print(f"[LEDService] ✅ Initialized GPIO pins: {self.PINS}")
        except Exception as e:
            print(f"[LEDService] ⚠️ GPIO setup failed: {e}")
            self._gpio_available = False

    def stop_blink(self):
        """
        Stop any ongoing blink operation.
        This is called automatically before any LED state change.
        """
        # Signal the blink thread to stop
        self._stop_blink_flag.set()

        # Wait for the blink thread to finish (with timeout)
        if self._blink_thread and self._blink_thread.is_alive():
            self._blink_thread.join(timeout=1.0)
            print("[LEDService] Stopped ongoing blink operation")

        # Clear the flag for next use
        self._stop_blink_flag.clear()
        self._blink_thread = None

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

        # Stop any ongoing blink first
        self.stop_blink()

        pin = self.PINS[color]

        if not self._gpio_available:
            print(f"[LEDService] [MOCK] {color.upper()} LED {state.upper()}")
            return True

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
        """Turn off all LEDs and stop any blinking"""
        # Stop any ongoing blink first
        self.stop_blink()

        if not self._gpio_available:
            print("[LEDService] [MOCK] All LEDs OFF")
            return

        for color, pin in self.PINS.items():
            GPIO.output(pin, GPIO.LOW)
        print("[LEDService] All LEDs turned OFF")

    def _blink_worker(self, color: str, times: int, interval: float):
        """
        Worker function for blinking LED in a separate thread.
        Checks stop flag between each blink cycle.
        """
        if color not in self.PINS:
            return

        pin = self.PINS[color]

        for i in range(times):
            # Check if we should stop
            if self._stop_blink_flag.is_set():
                print(f"[LEDService] Blink interrupted at iteration {i}/{times}")
                if self._gpio_available:
                    GPIO.output(pin, GPIO.LOW)
                return

            if self._gpio_available:
                GPIO.output(pin, GPIO.HIGH)
            
            # Use short sleep intervals to check stop flag more frequently
            for _ in range(int(interval * 20)):  # Check every 50ms
                if self._stop_blink_flag.is_set():
                    if self._gpio_available:
                        GPIO.output(pin, GPIO.LOW)
                    print(f"[LEDService] Blink interrupted during ON phase")
                    return
                time.sleep(0.05)

            if self._gpio_available:
                GPIO.output(pin, GPIO.LOW)

            # Check stop flag during OFF phase too
            for _ in range(int(interval * 20)):
                if self._stop_blink_flag.is_set():
                    print(f"[LEDService] Blink interrupted during OFF phase")
                    return
                time.sleep(0.05)

        print(f"[LEDService] {color.upper()} LED blink completed ({times} times)")

    def blink(self, color: str, times: int = 3, interval: float = 0.3) -> bool:
        """
        Blink a specific LED (non-blocking).
        
        The blink runs in a background thread and can be interrupted by:
        - Calling stop_blink()
        - Calling turn_off_all()
        - Starting a new LED operation (set_led, set_color_exclusive, etc.)

        Args:
            color: LED color ('green', 'yellow', 'red')
            times: Number of blinks (default: 3)
            interval: Time between blinks in seconds (default: 0.3)

        Returns:
            bool: True if blink started successfully, False if invalid color
        """
        color = color.lower()

        if color not in self.PINS:
            print(f"[LEDService] ERROR: Unknown color '{color}'")
            return False

        # Stop any ongoing blink first
        self.stop_blink()

        pin = self.PINS[color]
        print(f"[LEDService] {color.upper()} LED (GPIO {pin}) starting blink ({times} times, {interval}s interval)")

        # Start blink in a background thread
        self._blink_thread = threading.Thread(
            target=self._blink_worker,
            args=(color, times, interval),
            daemon=True
        )
        self._blink_thread.start()

        return True

    def blink_sync(self, color: str, times: int = 3, interval: float = 0.3) -> bool:
        """
        Blink a specific LED (blocking/synchronous version).
        Use this only when you specifically need blocking behavior.

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

        # Stop any ongoing blink first
        self.stop_blink()

        pin = self.PINS[color]
        print(f"[LEDService] {color.upper()} LED blinking {times} times (sync)")

        if not self._gpio_available:
            # In mock mode, just sleep
            for i in range(times):
                if self._stop_blink_flag.is_set():
                    return True
                time.sleep(interval * 2)
            return True

        for i in range(times):
            if self._stop_blink_flag.is_set():
                GPIO.output(pin, GPIO.LOW)
                return True
            GPIO.output(pin, GPIO.HIGH)
            time.sleep(interval)
            GPIO.output(pin, GPIO.LOW)
            time.sleep(interval)

        return True

    def set_color_exclusive(self, color: str) -> bool:
        """
        Turn on a specific LED and turn off all others.
        Stops any ongoing blink operation.

        Args:
            color: LED color to turn on ('green', 'yellow', 'red')

        Returns:
            bool: True if successful, False if invalid color
        """
        color = color.lower()

        if color not in self.PINS:
            print(f"[LEDService] ERROR: Unknown color '{color}'")
            return False

        # Stop any ongoing blink first
        self.stop_blink()

        pin = self.PINS[color]

        if not self._gpio_available:
            print(f"[LEDService] [MOCK] {color.upper()} LED ON (exclusive)")
            return True

        # Turn off all LEDs first
        for c, p in self.PINS.items():
            GPIO.output(p, GPIO.LOW)

        # Turn on the requested LED
        GPIO.output(pin, GPIO.HIGH)
        print(f"[LEDService] {color.upper()} LED (GPIO {pin}) turned ON (exclusive)")

        return True

    def cleanup(self):
        """Clean up GPIO resources"""
        self.stop_blink()
        self.turn_off_all()
        if self._gpio_available:
            GPIO.cleanup()
            print("[LEDService] GPIO cleaned up")
        else:
            print("[LEDService] [MOCK] Cleanup complete")

    def get_pin(self, color: str) -> int:
        """
        Get the GPIO pin number for a color

        Args:
            color: LED color ('green', 'yellow', 'red')

        Returns:
            int: GPIO pin number, or None if invalid color
        """
        return self.PINS.get(color.lower())

    def is_blinking(self) -> bool:
        """Check if a blink operation is currently running"""
        return self._blink_thread is not None and self._blink_thread.is_alive()


# Example usage
if __name__ == "__main__":
    import sys

    led = LEDService()

    try:
        print("\nTesting LED Service (non-blocking blink)...")
        print("=" * 50)

        # Test non-blocking blink
        print("\n1. Starting yellow blink (should be non-blocking)...")
        led.blink("yellow", times=10, interval=0.5)
        print("   Blink started, waiting 2 seconds...")
        time.sleep(2)

        print("\n2. Interrupting with green ON...")
        led.set_color_exclusive("green")
        time.sleep(1)

        print("\n3. Starting red blink...")
        led.blink("red", times=5, interval=0.3)
        time.sleep(1)

        print("\n4. Turning off all LEDs...")
        led.turn_off_all()
        time.sleep(0.5)

        print("\n" + "=" * 50)
        print("LED Service test complete!")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    finally:
        led.cleanup()
