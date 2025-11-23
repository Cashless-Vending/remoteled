"""
Locations API endpoints for managing location reference data
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.core.database import db
from app.models.schemas import (
    LocationCreate,
    LocationUpdate,
    LocationResponse,
    ErrorResponse
)

router = APIRouter()


@router.get("/all", response_model=List[LocationResponse])
def get_all_locations():
    """Get all locations"""
    query = """
        SELECT id, name, description, created_at
        FROM locations
        ORDER BY name ASC
    """
    with db.get_cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(location_id: str):
    """Get a specific location by ID"""
    query = """
        SELECT id, name, description, created_at
        FROM locations
        WHERE id = %s
    """
    with db.get_cursor() as cursor:
        cursor.execute(query, (location_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Location not found")
        return dict(row)


@router.post("", response_model=LocationResponse, status_code=201)
def create_location(location: LocationCreate):
    """Create a new location"""
    query = """
        INSERT INTO locations (name, description)
        VALUES (%s, %s)
        RETURNING id, name, description, created_at
    """
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, (location.name, location.description))
            row = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
    except Exception as e:
        if "unique" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail=f"Location with name '{location.name}' already exists"
            )
        raise HTTPException(status_code=500, detail=f"Failed to create location: {str(e)}")


@router.patch("/{location_id}", response_model=LocationResponse)
def update_location(location_id: str, location: LocationUpdate):
    """Update an existing location"""
    # Build dynamic update query
    updates = []
    values = []
    
    if location.name is not None:
        updates.append("name = %s")
        values.append(location.name)
    
    if location.description is not None:
        updates.append("description = %s")
        values.append(location.description)
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    values.append(location_id)
    query = f"""
        UPDATE locations
        SET {', '.join(updates)}
        WHERE id = %s
        RETURNING id, name, description, created_at
    """
    
    try:
        with db.get_cursor() as cursor:
            cursor.execute(query, tuple(values))
            row = cursor.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Location not found")
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
    except HTTPException:
        raise
    except Exception as e:
        if "unique" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail=f"Location with name '{location.name}' already exists"
            )
        raise HTTPException(status_code=500, detail=f"Failed to update location: {str(e)}")


@router.delete("/{location_id}", status_code=204)
def delete_location(location_id: str):
    """Delete a location"""
    # Check if any devices are using this location
    check_query = """
        SELECT COUNT(*) as count
        FROM devices
        WHERE location_id = %s
    """
    
    delete_query = """
        DELETE FROM locations
        WHERE id = %s
        RETURNING id
    """
    
    with db.get_cursor() as cursor:
        # Check for dependencies
        cursor.execute(check_query, (location_id,))
        result = cursor.fetchone()
        if result[0] > 0:
            raise HTTPException(
                status_code=409,
                detail=f"Cannot delete location: {result[0]} device(s) are using this location"
            )
        
        # Delete the location
        cursor.execute(delete_query, (location_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Location not found")
