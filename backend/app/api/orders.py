"""
Order API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from app.core.database import get_db
from app.models.schemas import (
    OrderCreateRequest, OrderResponse, OrderStatusUpdateRequest, OrderStatus
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(order_req: OrderCreateRequest, cursor: RealDictCursor = Depends(get_db)):
    """
    Create a new order
    
    Flow:
    1. Validate device exists
    2. Validate service exists and is active
    3. Calculate authorized minutes based on service type
    4. Create order with status CREATED
    """
    # Validate device exists
    cursor.execute("SELECT id FROM devices WHERE id = %s", (order_req.device_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Device not found")
    
    # Get service details
    cursor.execute(
        """
        SELECT type, price_cents, fixed_minutes, minutes_per_25c, active
        FROM services
        WHERE id = %s AND device_id = %s
        """,
        (order_req.product_id, order_req.device_id)
    )
    
    service = cursor.fetchone()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    if not service['active']:
        raise HTTPException(status_code=400, detail="Service is not active")
    
    # Calculate authorized minutes based on service type
    service_type = service['type']
    authorized_minutes = 0
    
    if service_type == "TRIGGER":
        # TRIGGER: no duration, instant activation
        authorized_minutes = 0
    elif service_type == "FIXED":
        # FIXED: use the fixed_minutes value
        authorized_minutes = service['fixed_minutes']
    elif service_type == "VARIABLE":
        # VARIABLE: calculate based on amount paid
        quarters = order_req.amount_cents // 25
        authorized_minutes = quarters * service['minutes_per_25c']
    
    # Create order
    cursor.execute(
        """
        INSERT INTO orders (device_id, product_id, amount_cents, authorized_minutes, status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, device_id, product_id, amount_cents, authorized_minutes, 
                  status, created_at, updated_at
        """,
        (order_req.device_id, order_req.product_id, order_req.amount_cents, 
         authorized_minutes, OrderStatus.CREATED.value)
    )
    
    order = cursor.fetchone()
    return order


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, cursor: RealDictCursor = Depends(get_db)):
    """Get order by ID"""
    cursor.execute(
        """
        SELECT id, device_id, product_id, amount_cents, authorized_minutes,
               status, created_at, updated_at
        FROM orders
        WHERE id = %s
        """,
        (order_id,)
    )
    
    order = cursor.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdateRequest,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Update order status
    
    Valid transitions:
    - CREATED -> PAID (after payment)
    - PAID -> RUNNING (device activated)
    - RUNNING -> DONE (session complete)
    - PAID/RUNNING -> FAILED (error occurred)
    """
    # Get current order
    cursor.execute("SELECT status FROM orders WHERE id = %s", (order_id,))
    order = cursor.fetchone()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    current_status = order['status']
    new_status = status_update.status.value
    
    # Validate status transition
    valid_transitions = {
        "CREATED": ["PAID", "FAILED"],
        "PAID": ["RUNNING", "FAILED"],
        "RUNNING": ["DONE", "FAILED"],
        "DONE": [],  # Terminal state
        "FAILED": []  # Terminal state
    }
    
    if new_status not in valid_transitions.get(current_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from {current_status} to {new_status}"
        )
    
    # Update status
    cursor.execute(
        """
        UPDATE orders
        SET status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING id, device_id, product_id, amount_cents, authorized_minutes,
                  status, created_at, updated_at
        """,
        (new_status, order_id)
    )
    
    updated_order = cursor.fetchone()
    return updated_order

