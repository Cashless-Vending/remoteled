"""
Telemetry/Logging API endpoints
"""
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from app.core.database import get_db
from app.core.validators import validate_uuid
from app.models.schemas import TelemetryRequest, LogResponse, OrderStatus
from app.services.crypto import crypto_service
from app.core import led_handler

router = APIRouter(prefix="/devices", tags=["telemetry"])


@router.post("/{device_id}/telemetry", response_model=dict, status_code=201)
async def create_telemetry_log(
    device_id: str,
    telemetry: TelemetryRequest,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Log telemetry event from device via mobile app
    
    Events:
    - STARTED: Device has been activated and started
    - DONE: Device session completed successfully
    - ERROR: Device encountered an error
    
    This also updates the order status based on the event.
    """
    # Validate UUID format
    validate_uuid(device_id, "Device ID")
    if telemetry.order_id:
        validate_uuid(telemetry.order_id, "Order ID")
    
    # Validate device exists
    cursor.execute("SELECT id FROM devices WHERE id = %s", (device_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Determine if event was successful
    ok = telemetry.event in ["STARTED", "DONE"]
    
    # Create hash if not provided
    payload_hash = telemetry.payload_hash
    if not payload_hash and telemetry.order_id:
        payload_hash = f"sha256:{crypto_service.generate_nonce()}"
    
    # Log the event
    cursor.execute(
        """
        INSERT INTO logs (device_id, direction, payload_hash, ok, details)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, device_id, direction, payload_hash, ok, details, created_at
        """,
        (device_id, "PI_TO_SRV", payload_hash, ok, 
         telemetry.details or f"{telemetry.event} event received")
    )
    
    log = cursor.fetchone()
    
    # Update order status based on event and trigger LED
    if telemetry.order_id:
        new_status = None

        if telemetry.event == "STARTED":
            new_status = OrderStatus.RUNNING.value
        elif telemetry.event == "DONE":
            new_status = OrderStatus.DONE.value
        elif telemetry.event == "ERROR":
            new_status = OrderStatus.FAILED.value

        if new_status:
            cursor.execute(
                """
                UPDATE orders
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND device_id = %s
                """,
                (new_status, telemetry.order_id, device_id)
            )

            # Trigger LED based on event type
            if telemetry.event == "STARTED":
                # Device started - turn LED ON solid
                # Get service type to determine color
                cursor.execute(
                    """
                    SELECT s.type
                    FROM orders o
                    JOIN services s ON o.service_id = s.id
                    WHERE o.id = %s
                    """,
                    (telemetry.order_id,)
                )
                order_service = cursor.fetchone()
                if order_service:
                    service_type = order_service['type']
                    led_color = led_handler.get_led_color_for_service_type(service_type)
                    print(f"[Telemetry] Device STARTED → LED SOLID ON ({led_color.upper()} for {service_type})")
                    # Trigger in background
                    asyncio.create_task(trigger_led_on_background(led_color, device_id))

            elif telemetry.event == "DONE":
                # Device finished - turn LED OFF
                print(f"[Telemetry] Device DONE → LED OFF")
                # Trigger in background
                asyncio.create_task(trigger_led_off_background(device_id))

    return {
        "success": True,
        "log_id": log['id'],
        "message": f"Telemetry event {telemetry.event} logged successfully"
    }


async def trigger_led_on_background(color: str, device_id: str):
    """Helper to trigger LED ON in background"""
    try:
        await led_handler.trigger_led_on(color=color)
    except Exception as e:
        print(f"[Telemetry LED] Error turning LED ON: {e}")


async def trigger_led_off_background(device_id: str):
    """Helper to trigger LED OFF in background"""
    try:
        await led_handler.trigger_led_off()
    except Exception as e:
        print(f"[Telemetry LED] Error turning LED OFF: {e}")


@router.get("/{device_id}/logs", response_model=list)
def get_device_logs(
    device_id: str,
    limit: int = 50,
    cursor: RealDictCursor = Depends(get_db)
):
    """Get recent logs for a device"""
    # Validate UUID format
    validate_uuid(device_id, "Device ID")
    
    # Validate device exists
    cursor.execute("SELECT id FROM devices WHERE id = %s", (device_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Device not found")
    
    cursor.execute(
        """
        SELECT id, device_id, direction, payload_hash, ok, details, created_at
        FROM logs
        WHERE device_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (device_id, limit)
    )
    
    logs = cursor.fetchall()
    return logs

