"""
Payment API endpoints (Mock implementation for development)
"""
from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from app.core.database import get_db
from app.core.config import settings
from app.models.schemas import (
    PaymentIntentRequest, PaymentIntentResponse, MockPaymentRequest, OrderStatus
)

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/intent", response_model=PaymentIntentResponse)
def create_payment_intent(
    payment_req: PaymentIntentRequest,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Create a payment intent (mock for development)
    
    In production, this would integrate with Stripe or another payment processor
    """
    # Validate order exists
    cursor.execute(
        "SELECT id, status, amount_cents FROM orders WHERE id = %s",
        (payment_req.order_id,)
    )
    
    order = cursor.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order['status'] != OrderStatus.CREATED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Order must be in CREATED status. Current: {order['status']}"
        )
    
    # Validate amount matches
    if order['amount_cents'] != payment_req.amount_cents:
        raise HTTPException(
            status_code=400,
            detail=f"Amount mismatch. Order: {order['amount_cents']}, Request: {payment_req.amount_cents}"
        )
    
    return PaymentIntentResponse(
        order_id=payment_req.order_id,
        amount_cents=payment_req.amount_cents,
        payment_method="mock",
        status="ready"
    )


@router.post("/mock", response_model=dict)
def process_mock_payment(
    mock_req: MockPaymentRequest,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Process a mock payment (for development/testing only)
    
    This simulates successful payment processing.
    Set success=False to simulate payment failure.
    """
    if not settings.ENABLE_MOCK_PAYMENT:
        raise HTTPException(
            status_code=403,
            detail="Mock payments are disabled in this environment"
        )
    
    # Get order
    cursor.execute(
        "SELECT id, status, amount_cents FROM orders WHERE id = %s",
        (mock_req.order_id,)
    )
    
    order = cursor.fetchone()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order['status'] != OrderStatus.CREATED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Order must be in CREATED status. Current: {order['status']}"
        )
    
    if mock_req.success:
        # Update order to PAID
        cursor.execute(
            """
            UPDATE orders
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (OrderStatus.PAID.value, mock_req.order_id)
        )
        
        return {
            "success": True,
            "order_id": mock_req.order_id,
            "amount_cents": order['amount_cents'],
            "message": "Mock payment processed successfully",
            "status": "PAID"
        }
    else:
        # Simulate payment failure
        cursor.execute(
            """
            UPDATE orders
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (OrderStatus.FAILED.value, mock_req.order_id)
        )
        
        return {
            "success": False,
            "order_id": mock_req.order_id,
            "message": "Mock payment failed (simulated)",
            "status": "FAILED"
        }

