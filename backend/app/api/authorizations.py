"""
Authorization API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.config import settings
from app.core.validators import validate_uuid
from app.models.schemas import (
    AuthorizationCreateRequest, AuthorizationResponse, 
    AuthorizationPayload, OrderStatus
)
from app.services.crypto import crypto_service

router = APIRouter(prefix="/authorizations", tags=["authorizations"])


@router.post("", response_model=AuthorizationResponse, status_code=201)
def create_authorization(
    auth_req: AuthorizationCreateRequest,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Create a signed authorization for a paid order
    
    Flow:
    1. Validate order exists and is PAID
    2. Get service type and authorized minutes
    3. Create authorization payload
    4. Sign payload with ECDSA
    5. Store authorization in database
    6. Return signed authorization to client
    """
    # Get order details
    cursor.execute(
        """
        SELECT o.id, o.device_id, o.service_id, o.authorized_minutes, o.status,
               s.type as service_type
        FROM orders o
        JOIN services s ON o.service_id = s.id
        WHERE o.id = %s
        """,
        (auth_req.order_id,)
    )
    
    order = cursor.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Validate order status
    if order['status'] != OrderStatus.PAID.value:
        raise HTTPException(
            status_code=400,
            detail=f"Order must be PAID to create authorization. Current status: {order['status']}"
        )
    
    # Check if authorization already exists
    cursor.execute(
        "SELECT id FROM authorizations WHERE order_id = %s",
        (auth_req.order_id,)
    )
    if cursor.fetchone():
        raise HTTPException(
            status_code=400,
            detail="Authorization already exists for this order"
        )
    
    # Calculate seconds from minutes
    authorized_seconds = order['authorized_minutes'] * 60
    
    # For TRIGGER type, use 2 seconds
    if order['service_type'] == 'TRIGGER':
        authorized_seconds = 2
    
    # Create authorization payload
    payload_dict = crypto_service.create_payload(
        device_id=order['device_id'],
        order_id=order['id'],
        service_type=order['service_type'],
        authorized_seconds=authorized_seconds
    )
    
    # Sign payload
    signature_hex = crypto_service.sign_payload(payload_dict)
    
    # Calculate expiry time
    expires_at = datetime.utcnow() + timedelta(minutes=settings.AUTH_EXPIRY_MINUTES)
    
    # Store authorization
    cursor.execute(
        """
        INSERT INTO authorizations (order_id, device_id, payload_json, signature_hex, expires_at)
        VALUES (%s, %s, %s::jsonb, %s, %s)
        RETURNING id, order_id, device_id, payload_json, signature_hex, expires_at, created_at
        """,
        (order['id'], order['device_id'], 
         str(payload_dict).replace("'", '"'),  # Convert to JSON string
         signature_hex, expires_at)
    )
    
    authorization = cursor.fetchone()
    
    # Parse payload_json back to dict
    import json
    auth_response = dict(authorization)
    auth_response['payload'] = json.loads(str(authorization['payload_json']).replace("'", '"'))
    
    return auth_response


@router.get("/{authorization_id}", response_model=AuthorizationResponse)
def get_authorization(authorization_id: str, cursor: RealDictCursor = Depends(get_db)):
    """Get authorization by ID"""
    # Validate UUID format
    validate_uuid(authorization_id, "Authorization ID")
    
    cursor.execute(
        """
        SELECT id, order_id, device_id, payload_json, signature_hex, expires_at, created_at
        FROM authorizations
        WHERE id = %s
        """,
        (authorization_id,)
    )
    
    authorization = cursor.fetchone()
    if not authorization:
        raise HTTPException(status_code=404, detail="Authorization not found")
    
    # Parse payload_json
    import json
    auth_response = dict(authorization)
    auth_response['payload'] = json.loads(str(authorization['payload_json']).replace("'", '"'))
    
    return auth_response


@router.get("/order/{order_id}", response_model=AuthorizationResponse)
def get_authorization_by_order(order_id: str, cursor: RealDictCursor = Depends(get_db)):
    """Get authorization by order ID"""
    # Validate UUID format
    validate_uuid(order_id, "Order ID")
    
    cursor.execute(
        """
        SELECT id, order_id, device_id, payload_json, signature_hex, expires_at, created_at
        FROM authorizations
        WHERE order_id = %s
        """,
        (order_id,)
    )
    
    authorization = cursor.fetchone()
    if not authorization:
        raise HTTPException(status_code=404, detail="Authorization not found for this order")
    
    # Parse payload_json
    import json
    auth_response = dict(authorization)
    auth_response['payload'] = json.loads(str(authorization['payload_json']).replace("'", '"'))
    
    return auth_response

