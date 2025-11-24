"""
Reference Data API endpoints
Handles device models, locations, and service types
"""
from fastapi import APIRouter, Depends, HTTPException, status
from psycopg2.extras import RealDictCursor
import psycopg2.errors
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.admin_logger import log_admin_action

router = APIRouter(prefix="/admin", tags=["reference-data"])


# ============================================================
# DEVICE MODELS
# ============================================================

class DeviceModelCreate(BaseModel):
    name: str
    description: Optional[str] = None


class DeviceModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class DeviceModelResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: str


@router.get("/device-models", response_model=List[DeviceModelResponse])
async def get_device_models(
    cursor: RealDictCursor = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all device models"""
    cursor.execute("""
        SELECT id, name, description, created_at
        FROM device_models
        ORDER BY name
    """)
    models = cursor.fetchall()
    return [{
        'id': str(model['id']),
        'name': model['name'],
        'description': model['description'],
        'created_at': model['created_at'].isoformat() if model['created_at'] else None
    } for model in models]


@router.post("/device-models", response_model=DeviceModelResponse, status_code=status.HTTP_201_CREATED)
async def create_device_model(
    data: DeviceModelCreate,
    cursor: RealDictCursor = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new device model"""
    try:
        cursor.execute("""
            INSERT INTO device_models (name, description)
            VALUES (%s, %s)
            RETURNING id, name, description, created_at
        """, (data.name, data.description))
        
        model = cursor.fetchone()
        
        if not model:
            raise HTTPException(status_code=500, detail="Failed to create device model")
        
        cursor.connection.commit()
        
        log_admin_action(
            admin_email=current_user.get('email', 'unknown'),
            action='CREATE',
            entity_type='device_model',
            entity_id=str(model['id']),
            admin_id=current_user.get('id')
        )
        
        return {
            'id': str(model['id']),
            'name': model['name'],
            'description': model['description'],
            'created_at': model['created_at'].isoformat() if model.get('created_at') else None
        }
    except HTTPException:
        raise
    except Exception as e:
        cursor.connection.rollback()
        error_msg = str(e)
        # Check if this is a unique constraint violation
        if "unique constraint" in error_msg.lower() or isinstance(e, psycopg2.errors.UniqueViolation):
            raise HTTPException(status_code=409, detail=f"A device model with this name already exists")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/device-models/{model_id}", response_model=DeviceModelResponse)
async def update_device_model(
    model_id: str,
    data: DeviceModelUpdate,
    cursor: RealDictCursor = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a device model"""
    # Check if model exists
    cursor.execute("SELECT id FROM device_models WHERE id = %s", (model_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Device model not found")
    
    # Build update query dynamically
    updates = []
    params = []
    
    if data.name is not None:
        updates.append("name = %s")
        params.append(data.name)
    
    if data.description is not None:
        updates.append("description = %s")
        params.append(data.description)
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    params.append(model_id)
    
    try:
        cursor.execute(f"""
            UPDATE device_models
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, name, description, created_at
        """, params)
        
        cursor.connection.commit()
        model = cursor.fetchone()
        
        log_admin_action(
            admin_email=current_user.get('email', 'unknown'),
            action='UPDATE',
            entity_type='device_model',
            entity_id=model_id,
            admin_id=current_user.get('id')
        )
        
        return {
            'id': str(model['id']),
            'name': model['name'],
            'description': model['description'],
            'created_at': model['created_at'].isoformat() if model['created_at'] else None
        }
    except Exception as e:
        cursor.connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/device-models/{model_id}")
async def delete_device_model(
    model_id: str,
    cursor: RealDictCursor = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a device model"""
    # Check if model exists
    cursor.execute("SELECT name FROM device_models WHERE id = %s", (model_id,))
    model = cursor.fetchone()
    if not model:
        raise HTTPException(status_code=404, detail="Device model not found")
    
    try:
        cursor.execute("DELETE FROM device_models WHERE id = %s", (model_id,))
        cursor.connection.commit()
        
        log_admin_action(
            admin_email=current_user.get('email', 'unknown'),
            action='DELETE',
            entity_type='device_model',
            entity_id=model_id,
            admin_id=current_user.get('id')
        )
        
        return {"success": True, "message": f"Device model '{model['name']}' deleted"}
    except Exception as e:
        cursor.connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# LOCATIONS
# ============================================================

class LocationCreate(BaseModel):
    name: str
    description: Optional[str] = None


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class LocationResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: str


@router.get("/locations", response_model=List[LocationResponse])
async def get_locations(
    cursor: RealDictCursor = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all locations"""
    cursor.execute("""
        SELECT id, name, description, created_at
        FROM locations
        ORDER BY name
    """)
    locations = cursor.fetchall()
    return [{
        'id': str(loc['id']),
        'name': loc['name'],
        'description': loc['description'],
        'created_at': loc['created_at'].isoformat() if loc['created_at'] else None
    } for loc in locations]


@router.post("/locations", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    data: LocationCreate,
    cursor: RealDictCursor = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new location"""
    try:
        cursor.execute("""
            INSERT INTO locations (name, description)
            VALUES (%s, %s)
            RETURNING id, name, description, created_at
        """, (data.name, data.description))
        
        location = cursor.fetchone()
        
        if not location:
            raise HTTPException(status_code=500, detail="Failed to create location")
        
        cursor.connection.commit()
        
        log_admin_action(
            admin_email=current_user.get('email', 'unknown'),
            action='CREATE',
            entity_type='location',
            entity_id=str(location['id']),
            admin_id=current_user.get('id')
        )
        
        return {
            'id': str(location['id']),
            'name': location['name'],
            'description': location['description'],
            'created_at': location['created_at'].isoformat() if location.get('created_at') else None
        }
    except HTTPException:
        raise
    except Exception as e:
        cursor.connection.rollback()
        error_msg = str(e)
        # Check if this is a unique constraint violation
        if "unique constraint" in error_msg.lower() or isinstance(e, psycopg2.errors.UniqueViolation):
            raise HTTPException(status_code=409, detail=f"A location with this name already exists")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/locations/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: str,
    data: LocationUpdate,
    cursor: RealDictCursor = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a location"""
    # Check if location exists
    cursor.execute("SELECT id FROM locations WHERE id = %s", (location_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Location not found")
    
    # Build update query dynamically
    updates = []
    params = []
    
    if data.name is not None:
        updates.append("name = %s")
        params.append(data.name)
    
    if data.description is not None:
        updates.append("description = %s")
        params.append(data.description)
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    params.append(location_id)
    
    try:
        cursor.execute(f"""
            UPDATE locations
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, name, description, created_at
        """, params)
        
        cursor.connection.commit()
        location = cursor.fetchone()
        
        log_admin_action(
            admin_email=current_user.get('email', 'unknown'),
            action='UPDATE',
            entity_type='location',
            entity_id=location_id,
            admin_id=current_user.get('id')
        )
        
        return {
            'id': str(location['id']),
            'name': location['name'],
            'description': location['description'],
            'created_at': location['created_at'].isoformat() if location['created_at'] else None
        }
    except Exception as e:
        cursor.connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/locations/{location_id}")
async def delete_location(
    location_id: str,
    cursor: RealDictCursor = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a location"""
    # Check if location exists
    cursor.execute("SELECT name FROM locations WHERE id = %s", (location_id,))
    location = cursor.fetchone()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    try:
        cursor.execute("DELETE FROM locations WHERE id = %s", (location_id,))
        cursor.connection.commit()
        
        log_admin_action(
            admin_email=current_user.get('email', 'unknown'),
            action='DELETE',
            entity_type='location',
            entity_id=location_id,
            admin_id=current_user.get('id')
        )
        
        return {"success": True, "message": f"Location '{location['name']}' deleted"}
    except Exception as e:
        cursor.connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# SERVICE TYPES
# ============================================================

class ServiceTypeCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class ServiceTypeUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None


class ServiceTypeResponse(BaseModel):
    id: str
    name: str
    code: str
    description: Optional[str]
    created_at: str


@router.get("/service-types", response_model=List[ServiceTypeResponse])
async def get_service_types(
    cursor: RealDictCursor = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all service types"""
    cursor.execute("""
        SELECT id, name, code, description, created_at
        FROM service_types
        ORDER BY name
    """)
    types = cursor.fetchall()
    return [{
        'id': str(t['id']),
        'name': t['name'],
        'code': t['code'],
        'description': t['description'],
        'created_at': t['created_at'].isoformat() if t['created_at'] else None
    } for t in types]


@router.post("/service-types", response_model=ServiceTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_service_type(
    data: ServiceTypeCreate,
    cursor: RealDictCursor = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new service type"""
    try:
        cursor.execute("""
            INSERT INTO service_types (name, code, description)
            VALUES (%s, %s, %s)
            RETURNING id, name, code, description, created_at
        """, (data.name, data.code, data.description))
        
        service_type = cursor.fetchone()
        
        if not service_type:
            raise HTTPException(status_code=500, detail="Failed to create service type")
        
        cursor.connection.commit()
        
        log_admin_action(
            admin_email=current_user.get('email', 'unknown'),
            action='CREATE',
            entity_type='service_type',
            entity_id=str(service_type['id']),
            admin_id=current_user.get('id')
        )
        
        return {
            'id': str(service_type['id']),
            'name': service_type['name'],
            'code': service_type['code'],
            'description': service_type['description'],
            'created_at': service_type['created_at'].isoformat() if service_type.get('created_at') else None
        }
    except HTTPException:
        raise
    except Exception as e:
        cursor.connection.rollback()
        error_msg = str(e)
        # Check if this is a unique constraint violation
        if "unique constraint" in error_msg.lower() or isinstance(e, psycopg2.errors.UniqueViolation):
            raise HTTPException(status_code=409, detail=f"A service type with this name or code already exists")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/service-types/{type_id}", response_model=ServiceTypeResponse)
async def update_service_type(
    type_id: str,
    data: ServiceTypeUpdate,
    cursor: RealDictCursor = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a service type"""
    # Check if type exists
    cursor.execute("SELECT id FROM service_types WHERE id = %s", (type_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Service type not found")
    
    # Build update query dynamically
    updates = []
    params = []
    
    if data.name is not None:
        updates.append("name = %s")
        params.append(data.name)
    
    if data.code is not None:
        updates.append("code = %s")
        params.append(data.code)
    
    if data.description is not None:
        updates.append("description = %s")
        params.append(data.description)
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    params.append(type_id)
    
    try:
        cursor.execute(f"""
            UPDATE service_types
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, name, code, description, created_at
        """, params)
        
        cursor.connection.commit()
        service_type = cursor.fetchone()
        
        log_admin_action(
            admin_email=current_user.get('email', 'unknown'),
            action='UPDATE',
            entity_type='service_type',
            entity_id=type_id,
            admin_id=current_user.get('id')
        )
        
        return {
            'id': str(service_type['id']),
            'name': service_type['name'],
            'code': service_type['code'],
            'description': service_type['description'],
            'created_at': service_type['created_at'].isoformat() if service_type['created_at'] else None
        }
    except Exception as e:
        cursor.connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/service-types/{type_id}")
async def delete_service_type(
    type_id: str,
    cursor: RealDictCursor = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a service type"""
    # Check if type exists
    cursor.execute("SELECT name FROM service_types WHERE id = %s", (type_id,))
    service_type = cursor.fetchone()
    if not service_type:
        raise HTTPException(status_code=404, detail="Service type not found")
    
    try:
        cursor.execute("DELETE FROM service_types WHERE id = %s", (type_id,))
        cursor.connection.commit()
        
        log_admin_action(
            admin_email=current_user.get('email', 'unknown'),
            action='DELETE',
            entity_type='service_type',
            entity_id=type_id,
            admin_id=current_user.get('id')
        )
        
        return {"success": True, "message": f"Service type '{service_type['name']}' deleted"}
    except Exception as e:
        cursor.connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))

