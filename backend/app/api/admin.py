"""
Admin Console API endpoints
Dashboard statistics, analytics, and management
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.admin_logger import log_admin_action
from app.core.validators import validate_uuid
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter(prefix="/admin", tags=["admin"])


# Request models for device and service management
class DeviceCreateRequest(BaseModel):
    label: str
    public_key: str
    model: Optional[str] = None
    location: Optional[str] = None
    gpio_pin: Optional[int] = None


class DeviceUpdateRequest(BaseModel):
    label: Optional[str] = None
    model: Optional[str] = None
    location: Optional[str] = None
    gpio_pin: Optional[int] = None
    status: Optional[str] = None


class ServiceCreateRequest(BaseModel):
    device_id: str
    type: str  # TRIGGER, FIXED, VARIABLE
    price_cents: int
    fixed_minutes: Optional[int] = None
    minutes_per_25c: Optional[int] = None
    active: bool = True


class ServiceUpdateRequest(BaseModel):
    price_cents: Optional[int] = None
    fixed_minutes: Optional[int] = None
    minutes_per_25c: Optional[int] = None
    active: Optional[bool] = None


@router.get("/stats/overview")
def get_dashboard_stats(cursor: RealDictCursor = Depends(get_db)):
    """
    Get high-level dashboard statistics
    - Total devices (with change)
    - Active orders count
    - Revenue today
    - Success rate
    """
    
    # Total devices
    cursor.execute("SELECT COUNT(*) as total FROM devices WHERE status = 'ACTIVE'")
    total_devices = cursor.fetchone()['total']
    
    # Devices added this month
    cursor.execute("""
        SELECT COUNT(*) as new_this_month 
        FROM devices 
        WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE)
    """)
    new_devices = cursor.fetchone()['new_this_month']
    
    # Active orders (PAID or RUNNING)
    cursor.execute("""
        SELECT COUNT(*) as active 
        FROM orders 
        WHERE status IN ('PAID', 'RUNNING')
    """)
    active_orders = cursor.fetchone()['active']
    
    # Orders from last week for comparison
    cursor.execute("""
        SELECT COUNT(*) as last_week
        FROM orders
        WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
          AND created_at < CURRENT_DATE
          AND status IN ('PAID', 'RUNNING', 'DONE')
    """)
    last_week_orders = cursor.fetchone()['last_week']
    
    # Revenue today
    cursor.execute("""
        SELECT COALESCE(SUM(amount_cents), 0) as revenue
        FROM orders
        WHERE DATE(created_at) = CURRENT_DATE
          AND status IN ('PAID', 'RUNNING', 'DONE')
    """)
    revenue_today = cursor.fetchone()['revenue']
    
    # Revenue yesterday for comparison
    cursor.execute("""
        SELECT COALESCE(SUM(amount_cents), 0) as revenue
        FROM orders
        WHERE DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'
          AND status IN ('PAID', 'RUNNING', 'DONE')
    """)
    revenue_yesterday = cursor.fetchone()['revenue']
    
    # Success rate (last 100 orders)
    cursor.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE status = 'DONE') as successful,
            COUNT(*) as total
        FROM (
            SELECT status 
            FROM orders 
            ORDER BY created_at DESC 
            LIMIT 100
        ) recent_orders
    """)
    success_data = cursor.fetchone()
    success_rate = (success_data['successful'] / success_data['total'] * 100) if success_data['total'] > 0 else 0
    
    # Success rate from previous 100 orders
    cursor.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE status = 'DONE') as successful,
            COUNT(*) as total
        FROM (
            SELECT status 
            FROM orders 
            ORDER BY created_at DESC 
            OFFSET 100 LIMIT 100
        ) previous_orders
    """)
    prev_success_data = cursor.fetchone()
    prev_success_rate = (prev_success_data['successful'] / prev_success_data['total'] * 100) if prev_success_data['total'] > 0 else 0
    
    return {
        "total_devices": total_devices,
        "new_devices_this_month": new_devices,
        "active_orders": active_orders,
        "orders_change_percent": ((active_orders - last_week_orders) / last_week_orders * 100) if last_week_orders > 0 else 0,
        "revenue_today_cents": revenue_today,
        "revenue_change_percent": ((revenue_today - revenue_yesterday) / revenue_yesterday * 100) if revenue_yesterday > 0 else 0,
        "success_rate": round(success_rate, 1),
        "success_rate_change": round(success_rate - prev_success_rate, 1)
    }


@router.get("/stats/orders-last-7-days")
def get_orders_last_week(cursor: RealDictCursor = Depends(get_db)):
    """Get order counts for the last 7 days"""
    cursor.execute("""
        SELECT 
            TO_CHAR(date_series, 'Dy') as day_name,
            COALESCE(COUNT(o.id), 0) as order_count
        FROM generate_series(
            CURRENT_DATE - INTERVAL '6 days',
            CURRENT_DATE,
            INTERVAL '1 day'
        ) AS date_series
        LEFT JOIN orders o ON DATE(o.created_at) = date_series::date
        GROUP BY date_series
        ORDER BY date_series
    """)
    
    return cursor.fetchall()


@router.get("/stats/device-status")
def get_device_status_distribution(cursor: RealDictCursor = Depends(get_db)):
    """Get device status distribution"""
    cursor.execute("""
        SELECT 
            status,
            COUNT(*) as count
        FROM devices
        GROUP BY status
        ORDER BY count DESC
    """)
    
    return cursor.fetchall()


@router.get("/devices/all")
def get_all_devices(cursor: RealDictCursor = Depends(get_db)):
    """Get all devices with service counts and order stats"""
    cursor.execute("""
        SELECT 
            d.id,
            d.label,
            d.model,
            d.location,
            d.gpio_pin,
            d.status,
            d.created_at,
            COUNT(DISTINCT s.id) as service_count,
            COUNT(DISTINCT CASE WHEN s.active THEN s.id END) as active_service_count,
            COUNT(DISTINCT o.id) as total_orders,
            COUNT(DISTINCT CASE WHEN o.status = 'DONE' THEN o.id END) as completed_orders
        FROM devices d
        LEFT JOIN services s ON d.id = s.device_id
        LEFT JOIN orders o ON d.id = o.device_id
        GROUP BY d.id, d.label, d.model, d.location, d.gpio_pin, d.status, d.created_at
        ORDER BY d.created_at DESC
    """)
    
    return cursor.fetchall()


@router.get("/orders/recent")
def get_recent_orders(
    limit: int = Query(50, ge=1, le=500),
    cursor: RealDictCursor = Depends(get_db)
):
    """Get recent orders with device and product details"""
    cursor.execute("""
        SELECT 
            o.id,
            o.amount_cents,
            o.authorized_minutes,
            o.status,
            o.created_at,
            d.label as device_label,
            s.type as product_type
        FROM orders o
        JOIN devices d ON o.device_id = d.id
        JOIN services s ON o.product_id = s.id
        ORDER BY o.created_at DESC
        LIMIT %s
    """, (limit,))
    
    return cursor.fetchall()


@router.get("/services/all")
def get_all_services(cursor: RealDictCursor = Depends(get_db)):
    """Get all services/products with device info"""
    cursor.execute("""
        SELECT 
            s.id,
            s.type,
            s.price_cents,
            s.fixed_minutes,
            s.minutes_per_25c,
            s.active,
            s.created_at,
            d.label as device_label,
            d.id as device_id
        FROM services s
        JOIN devices d ON s.device_id = d.id
        ORDER BY d.label, s.price_cents
    """)
    
    return cursor.fetchall()


@router.get("/logs/recent")
def get_recent_logs(
    limit: int = Query(100, ge=1, le=500),
    error_only: bool = Query(False),
    cursor: RealDictCursor = Depends(get_db)
):
    """Get recent system logs"""
    query = """
        SELECT 
            l.id,
            l.direction,
            l.ok,
            l.details,
            l.created_at,
            d.label as device_label,
            d.id as device_id
        FROM logs l
        JOIN devices d ON l.device_id = d.id
    """
    
    if error_only:
        query += " WHERE l.ok = false"
    
    query += " ORDER BY l.created_at DESC LIMIT %s"
    
    cursor.execute(query, (limit,))
    
    return cursor.fetchall()


@router.get("/logs/admin-actions")
def get_admin_action_logs(
    limit: int = Query(100, ge=1, le=500),
    cursor: RealDictCursor = Depends(get_db)
):
    """Get recent admin action logs"""
    cursor.execute("""
        SELECT 
            id,
            admin_email,
            action,
            entity_type,
            entity_id,
            details,
            created_at
        FROM admin_logs
        ORDER BY created_at DESC
        LIMIT %s
    """, (limit,))
    
    return cursor.fetchall()


# ============================================================
# DEVICE MANAGEMENT ENDPOINTS
# ============================================================

@router.post("/devices")
def create_device(
    device: DeviceCreateRequest,
    current_user: dict = Depends(get_current_user),
    cursor: RealDictCursor = Depends(get_db)
):
    """Create a new device"""
    try:
        cursor.execute(
            """
            INSERT INTO devices (label, public_key, model, location, gpio_pin, status)
            VALUES (%s, %s, %s, %s, %s, 'ACTIVE')
            RETURNING id, label, model, location, gpio_pin, status, created_at
            """,
            (device.label, device.public_key, device.model, device.location, device.gpio_pin)
        )
        new_device = cursor.fetchone()
        cursor.connection.commit()
        
        # Log the action
        log_admin_action(
            admin_email=current_user['email'],
            action='CREATE_DEVICE',
            entity_type='device',
            entity_id=new_device['id'],
            details=f"Created device: {device.label}",
            admin_id=current_user['id']
        )
        
        return new_device
    except Exception as e:
        cursor.connection.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create device: {str(e)}")


@router.put("/devices/{device_id}")
def update_device(
    device_id: str,
    device: DeviceUpdateRequest,
    current_user: dict = Depends(get_current_user),
    cursor: RealDictCursor = Depends(get_db)
):
    """Update an existing device"""
    validate_uuid(device_id, "Device ID")
    
    # Build dynamic update query
    updates = []
    params = []
    
    if device.label is not None:
        updates.append("label = %s")
        params.append(device.label)
    if device.model is not None:
        updates.append("model = %s")
        params.append(device.model)
    if device.location is not None:
        updates.append("location = %s")
        params.append(device.location)
    if device.gpio_pin is not None:
        updates.append("gpio_pin = %s")
        params.append(device.gpio_pin)
    if device.status is not None:
        updates.append("status = %s")
        params.append(device.status)
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    params.append(device_id)
    
    try:
        cursor.execute(
            f"""
            UPDATE devices 
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, label, model, location, gpio_pin, status, created_at
            """,
            params
        )
        updated_device = cursor.fetchone()
        
        if not updated_device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        cursor.connection.commit()
        
        # Log the action
        log_admin_action(
            admin_email=current_user['email'],
            action='UPDATE_DEVICE',
            entity_type='device',
            entity_id=device_id,
            details=f"Updated device: {updated_device['label']}",
            admin_id=current_user['id']
        )
        
        return updated_device
    except HTTPException:
        raise
    except Exception as e:
        cursor.connection.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to update device: {str(e)}")


@router.delete("/devices/{device_id}")
def delete_device(
    device_id: str,
    current_user: dict = Depends(get_current_user),
    cursor: RealDictCursor = Depends(get_db)
):
    """Delete a device (and cascade to services)"""
    validate_uuid(device_id, "Device ID")
    
    try:
        cursor.execute("SELECT label FROM devices WHERE id = %s", (device_id,))
        device = cursor.fetchone()
        
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        
        cursor.execute("DELETE FROM devices WHERE id = %s", (device_id,))
        cursor.connection.commit()
        
        # Log the action
        log_admin_action(
            admin_email=current_user['email'],
            action='DELETE_DEVICE',
            entity_type='device',
            entity_id=device_id,
            details=f"Deleted device: {device['label']}",
            admin_id=current_user['id']
        )
        
        return {"success": True, "message": "Device deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        cursor.connection.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to delete device: {str(e)}")


# ============================================================
# SERVICE/PRODUCT MANAGEMENT ENDPOINTS
# ============================================================

@router.post("/services")
def create_service(
    service: ServiceCreateRequest,
    current_user: dict = Depends(get_current_user),
    cursor: RealDictCursor = Depends(get_db)
):
    """Create a new service/product"""
    validate_uuid(service.device_id, "Device ID")
    
    # Validate service type
    if service.type not in ['TRIGGER', 'FIXED', 'VARIABLE']:
        raise HTTPException(status_code=400, detail="Invalid service type")
    
    # Type-specific validations
    if service.type == 'TRIGGER':
        if service.fixed_minutes is not None or service.minutes_per_25c is not None:
            raise HTTPException(status_code=400, detail="TRIGGER services should not have duration fields")
    elif service.type == 'FIXED':
        if service.fixed_minutes is None:
            raise HTTPException(status_code=400, detail="FIXED services require fixed_minutes")
        if service.minutes_per_25c is not None:
            raise HTTPException(status_code=400, detail="FIXED services should not have minutes_per_25c")
    elif service.type == 'VARIABLE':
        if service.minutes_per_25c is None:
            raise HTTPException(status_code=400, detail="VARIABLE services require minutes_per_25c")
    
    try:
        cursor.execute(
            """
            INSERT INTO services (device_id, type, price_cents, fixed_minutes, minutes_per_25c, active)
            VALUES (%s, %s::service_type, %s, %s, %s, %s)
            RETURNING id, device_id, type, price_cents, fixed_minutes, minutes_per_25c, active, created_at
            """,
            (service.device_id, service.type, service.price_cents, service.fixed_minutes, service.minutes_per_25c, service.active)
        )
        new_service = cursor.fetchone()
        cursor.connection.commit()
        
        # Log the action
        log_admin_action(
            admin_email=current_user['email'],
            action='CREATE_SERVICE',
            entity_type='service',
            entity_id=new_service['id'],
            details=f"Created {service.type} service for device {service.device_id}",
            admin_id=current_user['id']
        )
        
        return new_service
    except Exception as e:
        cursor.connection.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to create service: {str(e)}")


@router.put("/services/{service_id}")
def update_service(
    service_id: str,
    service: ServiceUpdateRequest,
    current_user: dict = Depends(get_current_user),
    cursor: RealDictCursor = Depends(get_db)
):
    """Update an existing service/product"""
    validate_uuid(service_id, "Service ID")
    
    # Build dynamic update query
    updates = []
    params = []
    
    if service.price_cents is not None:
        updates.append("price_cents = %s")
        params.append(service.price_cents)
    if service.fixed_minutes is not None:
        updates.append("fixed_minutes = %s")
        params.append(service.fixed_minutes)
    if service.minutes_per_25c is not None:
        updates.append("minutes_per_25c = %s")
        params.append(service.minutes_per_25c)
    if service.active is not None:
        updates.append("active = %s")
        params.append(service.active)
    
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    params.append(service_id)
    
    try:
        cursor.execute(
            f"""
            UPDATE services 
            SET {', '.join(updates)}
            WHERE id = %s
            RETURNING id, device_id, type, price_cents, fixed_minutes, minutes_per_25c, active, created_at
            """,
            params
        )
        updated_service = cursor.fetchone()
        
        if not updated_service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        cursor.connection.commit()
        
        # Log the action
        log_admin_action(
            admin_email=current_user['email'],
            action='UPDATE_SERVICE',
            entity_type='service',
            entity_id=service_id,
            details=f"Updated service {service_id}",
            admin_id=current_user['id']
        )
        
        return updated_service
    except HTTPException:
        raise
    except Exception as e:
        cursor.connection.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to update service: {str(e)}")


@router.delete("/services/{service_id}")
def delete_service(
    service_id: str,
    current_user: dict = Depends(get_current_user),
    cursor: RealDictCursor = Depends(get_db)
):
    """Delete a service/product"""
    validate_uuid(service_id, "Service ID")
    
    try:
        cursor.execute("SELECT type FROM services WHERE id = %s", (service_id,))
        service = cursor.fetchone()
        
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Check if any orders reference this service
        cursor.execute("SELECT COUNT(*) as count FROM orders WHERE product_id = %s", (service_id,))
        order_count = cursor.fetchone()['count']
        
        if order_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete service: {order_count} order(s) still reference this product. Please delete or update those orders first."
            )
        
        cursor.execute("DELETE FROM services WHERE id = %s", (service_id,))
        cursor.connection.commit()
        
        # Log the action
        log_admin_action(
            admin_email=current_user['email'],
            action='DELETE_SERVICE',
            entity_type='service',
            entity_id=service_id,
            details=f"Deleted {service['type']} service",
            admin_id=current_user['id']
        )
        
        return {"success": True, "message": "Service deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        cursor.connection.rollback()
        raise HTTPException(status_code=400, detail=f"Failed to delete service: {str(e)}")


