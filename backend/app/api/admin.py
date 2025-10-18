"""
Admin Console API endpoints
Dashboard statistics, analytics, and management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from app.core.database import get_db
from datetime import datetime, timedelta

router = APIRouter(prefix="/admin", tags=["admin"])


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

