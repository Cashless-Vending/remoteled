"""
Payment API endpoints (Mock implementation for development)
"""
from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from app.core.database import get_db
from app.core.config import settings
from app.core.payment_handler import process_mock_payment as handle_mock_payment
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
async def process_mock_payment(
    mock_req: MockPaymentRequest,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Process a mock payment (for development/testing only)

    This simulates successful payment processing and triggers LED feedback.
    Set success=False to simulate payment failure.
    """
    # Use payment handler which will process payment and trigger LED
    result = await handle_mock_payment(mock_req, cursor, trigger_led_feedback=True)
    return result

