"""
Service Types API endpoints for managing service type reference data
Service types map user-friendly names to ENUM values (TRIGGER, FIXED, VARIABLE)
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.core.database import db
from app.models.schemas import (
    ServiceTypeCreate,
    ServiceTypeUpdate,
    ServiceTypeResponse,
    ErrorResponse
)

router = APIRouter()


@router.get("/all", response_model=List[ServiceTypeResponse])
def get_all_service_types():
    """Get all service types"""
    query = """
        SELECT id, name, code, description, created_at
        FROM service_types
        ORDER BY code ASC
    """
    with db.get_cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


@router.get("/{type_id}", response_model=ServiceTypeResponse)
def get_service_type(type_id: str):
    """Get a specific service type by ID"""
    query = """
        SELECT id, name, code, description, created_at
        FROM service_types
        WHERE id = %s
    """
    with db.get_cursor() as cursor:
        cursor.execute(query, (type_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Service type not found")
        return dict(row)


@router.post("", response_model=ServiceTypeResponse, status_code=201)
def create_service_type(service_type: ServiceTypeCreate):
    """Create a new service type"""
    query = """
        INSERT INTO service_types (name, code, description)
        VALUES (%s, %s, %s)
        RETURNING id, name, code, description, created_at
    """
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, (service_type.name, service_type.code, service_type.description))
            row = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
    except Exception as e:
        if "unique" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail=f"Service type with code '{service_type.code}' already exists"
            )
        raise HTTPException(status_code=500, detail=f"Failed to create service type: {str(e)}")


@router.patch("/{type_id}", response_model=ServiceTypeResponse)
def update_service_type(type_id: str, service_type: ServiceTypeUpdate):
    """Update an existing service type"""
    # Build dynamic update query
    updates = []
    values = []
    
    if service_type.name is not None:
        updates.append("name = %s")
        values.append(service_type.name)
    
    if service_type.code is not None:
        updates.append("code = %s")
        values.append(service_type.code)
    
    if service_type.description is not None:
        updates.append("description = %s")
        values.append(service_type.description)
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    values.append(type_id)
    query = f"""
        UPDATE service_types
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING id, name, code, description, created_at
    """
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, tuple(values))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Service type not found")
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
    except HTTPException:
        raise
    except Exception as e:
        if "unique" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail=f"Service type with code '{service_type.code}' already exists"
            )
        raise HTTPException(status_code=500, detail=f"Failed to update service type: {str(e)}")


@router.delete("/{type_id}", status_code=204)
def delete_service_type(type_id: str):
    """Delete a service type"""
    # Check if any services are using this service type
    check_query = """
        SELECT COUNT(*) as count
        FROM services
        WHERE type = (SELECT code FROM service_types WHERE id = %s)
    """
    
    delete_query = """
        DELETE FROM service_types
        WHERE id = %s
        RETURNING id
    """
    
    with db.get_cursor() as cursor:
        # Check for dependencies
        cursor.execute(check_query, (type_id,))
        result = cursor.fetchone()
        if result[0] > 0:
            raise HTTPException(
                status_code=409,
                detail=f"Cannot delete service type: {result[0]} service(s) are using this type"
            )
        
        # Delete the service type
        cursor.execute(delete_query, (type_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Service type not found")
