"""
Device API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from typing import List
from app.core.database import get_db
from app.core.validators import validate_uuid
from app.models.schemas import DeviceResponse, ServiceResponse, DeviceWithServicesResponse

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(device_id: str, cursor: RealDictCursor = Depends(get_db)):
    """Get device by ID"""
    # Validate UUID format
    validate_uuid(device_id, "Device ID")
    
    cursor.execute(
        """
        SELECT id, label, model, location, status, created_at
        FROM devices
        WHERE id = %s
        """,
        (device_id,)
    )
    
    device = cursor.fetchone()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return device


@router.get("/{device_id}/services", response_model=List[ServiceResponse])
def get_device_services(device_id: str, cursor: RealDictCursor = Depends(get_db)):
    """Get all active services/products for a device"""
    # Validate UUID format
    validate_uuid(device_id, "Device ID")
    
    # First verify device exists
    cursor.execute("SELECT id FROM devices WHERE id = %s", (device_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get active services
    cursor.execute(
        """
        SELECT id, device_id, type, price_cents, fixed_minutes, 
               minutes_per_25c, active, created_at
        FROM services
        WHERE device_id = %s AND active = true
        ORDER BY price_cents ASC
        """,
        (device_id,)
    )
    
    services = cursor.fetchall()
    return services


@router.get("/{device_id}/full", response_model=DeviceWithServicesResponse)
def get_device_with_services(device_id: str, cursor: RealDictCursor = Depends(get_db)):
    """Get device with all its services in one call"""
    # Validate UUID format
    validate_uuid(device_id, "Device ID")
    
    # Get device
    cursor.execute(
        """
        SELECT id, label, model, location, status, created_at
        FROM devices
        WHERE id = %s
        """,
        (device_id,)
    )
    
    device = cursor.fetchone()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get active services
    cursor.execute(
        """
        SELECT id, device_id, type, price_cents, fixed_minutes, 
               minutes_per_25c, active, created_at
        FROM services
        WHERE device_id = %s AND active = true
        ORDER BY price_cents ASC
        """,
        (device_id,)
    )
    
    services = cursor.fetchall()
    
    return {
        "device": device,
        "services": services
    }

