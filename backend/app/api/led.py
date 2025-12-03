"""
LED Control API - Direct LED control endpoints
"""
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core import led_handler

router = APIRouter(prefix="/led", tags=["led"])


class LEDControlRequest(BaseModel):
    color: str  # red, yellow, green
    mode: str   # blink, on, off


@router.post("/control")
async def control_led(request: LEDControlRequest):
    """
    Direct LED control endpoint

    Colors:
    - red: BLE connection indicator
    - yellow: Payment processing indicator
    - green: Device running indicator

    Modes:
    - blink: Blink the LED
    - on: Turn LED solid ON
    - off: Turn LED OFF
    """
    try:
        color = request.color.lower()
        mode = request.mode.lower()

        print(f"\n[LED Control] Request: {color.upper()} {mode.upper()}")

        if mode == "blink":
            # Continuous blink with many iterations - will stop when "off" command is sent
            success = await led_handler.trigger_led_blink(color=color, times=100, interval=0.5)
            return {"success": success, "message": f"{color} LED blinking"}
        elif mode == "on":
            success = await led_handler.trigger_led_on(color=color)
            return {"success": success, "message": f"{color} LED ON"}
        elif mode == "off":
            success = await led_handler.trigger_led_off()
            return {"success": success, "message": "LEDs OFF"}
        else:
            raise HTTPException(status_code=400, detail=f"Invalid mode: {mode}")

    except Exception as e:
        print(f"[LED Control] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/blink-stop")
async def stop_blink():
    """
    Stop any blinking LED by turning all LEDs off
    """
    try:
        success = await led_handler.trigger_led_off()
        return {"success": success, "message": "Blink stopped, LEDs OFF"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
