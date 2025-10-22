"""
Payment Handler - Process payments and trigger LED feedback
"""
import asyncio
from psycopg2.extras import RealDictCursor
from fastapi import HTTPException
from app.models.schemas import OrderStatus, MockPaymentRequest
from app.core.config import settings
from app.core.led_handler import trigger_led, get_led_color_for_status


async def process_mock_payment(
    mock_req: MockPaymentRequest,
    cursor: RealDictCursor,
    trigger_led_feedback: bool = True
) -> dict:
    """
    Process a mock payment and optionally trigger LED feedback

    Args:
        mock_req: Mock payment request with order_id and success flag
        cursor: Database cursor
        trigger_led_feedback: Whether to trigger LED feedback (default: True)

    Returns:
        dict: Payment result with status and details

    Raises:
        HTTPException: If payment processing fails
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

        result = {
            "success": True,
            "order_id": mock_req.order_id,
            "amount_cents": order['amount_cents'],
            "message": "Mock payment processed successfully",
            "status": "PAID"
        }

        # Trigger LED feedback for successful payment
        if trigger_led_feedback:
            color = get_led_color_for_status("success")
            asyncio.create_task(trigger_led(color, duration=10))

        return result
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

        result = {
            "success": False,
            "order_id": mock_req.order_id,
            "message": "Mock payment failed (simulated)",
            "status": "FAILED"
        }

        # Trigger LED feedback for failed payment
        if trigger_led_feedback:
            color = get_led_color_for_status("failed")
            asyncio.create_task(trigger_led(color, duration=10))

        return result


async def trigger_payment_led_feedback(status: str, duration: int = 10):
    """
    Trigger LED feedback based on payment status

    Args:
        status: Payment status (success, fail, processing)
        duration: How long to keep LED on (seconds, default 10)
    """
    color = get_led_color_for_status(status)
    await trigger_led(color, duration)
