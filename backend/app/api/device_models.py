"""
Device Models API endpoints for managing hardware model reference data
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.core.database import db
from app.models.schemas import (
    DeviceModelCreate,
    DeviceModelUpdate,
    DeviceModelResponse,
    ErrorResponse
)

router = APIRouter()


@router.get("/all", response_model=List[DeviceModelResponse])
def get_all_device_models():
    """Get all device models"""
    query = """
        SELECT id, name, description, created_at
        FROM device_models
        ORDER BY name ASC
    """
    with db.get_cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


@router.get("/{model_id}", response_model=DeviceModelResponse)
def get_device_model(model_id: str):
    """Get a specific device model by ID"""
    query = """
        SELECT id, name, description, created_at
        FROM device_models
        WHERE id = %s
    """
    with db.get_cursor() as cursor:
        cursor.execute(query, (model_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Device model not found")
        return dict(row)


@router.post("", response_model=DeviceModelResponse, status_code=201)
def create_device_model(model: DeviceModelCreate):
    """Create a new device model"""
    query = """
        INSERT INTO device_models (name, description)
        VALUES (%s, %s)
        RETURNING id, name, description, created_at
    """
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, (model.name, model.description))
            row = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
    except Exception as e:
        if "unique" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail=f"Device model with name '{model.name}' already exists"
            )
        raise HTTPException(status_code=500, detail=f"Failed to create device model: {str(e)}")


@router.patch("/{model_id}", response_model=DeviceModelResponse)
def update_device_model(model_id: str, model: DeviceModelUpdate):
    """Update an existing device model"""
    # Build dynamic update query
    updates = []
    values = []
    
    if model.name is not None:
        updates.append("name = %s")
        values.append(model.name)
    
    if model.description is not None:
        updates.append("description = %s")
        values.append(model.description)
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    values.append(model_id)
    query = f"""
        UPDATE device_models
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING id, name, description, created_at
    """
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, tuple(values))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Device model not found")
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
    except HTTPException:
        raise
    except Exception as e:
        if "unique" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail=f"Device model with name '{model.name}' already exists"
            )
        raise HTTPException(status_code=500, detail=f"Failed to update device model: {str(e)}")


@router.delete("/{model_id}", status_code=204)
def delete_device_model(model_id: str):
    """Delete a device model"""
    # Check if any devices are using this model
    check_query = """
        SELECT COUNT(*) as count
        FROM devices
        WHERE model_id = %s
    """
    
    delete_query = """
        DELETE FROM device_models
        WHERE id = %s
        RETURNING id
    """
    
    with db.get_cursor() as cursor:
        # Check for dependencies
        cursor.execute(check_query, (model_id,))
        result = cursor.fetchone()
        if result[0] > 0:
            raise HTTPException(
                status_code=409,
                detail=f"Cannot delete device model: {result[0]} device(s) are using this model"
            )
        
        # Delete the model
        cursor.execute(delete_query, (model_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Device model not found")

