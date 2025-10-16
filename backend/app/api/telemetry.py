"""
Telemetry/Logging API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from app.core.database import get_db
from app.core.validators import validate_uuid
from app.models.schemas import TelemetryRequest, LogResponse, OrderStatus
from app.services.crypto import crypto_service

router = APIRouter(prefix="/devices", tags=["telemetry"])


@router.post("/{device_id}/telemetry", response_model=dict, status_code=201)
def create_telemetry_log(
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
    
    # Update order status based on event
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
    
    return {
        "success": True,
        "log_id": log['id'],
        "message": f"Telemetry event {telemetry.event} logged successfully"
    }


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

