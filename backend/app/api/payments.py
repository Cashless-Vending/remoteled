"""
Payment API endpoints (Mock implementation for development)
"""
from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from app.core.database import get_db
from app.models.schemas import (
    CustomerRequest, CustomerResponse,
    StripePaymentRequest, StripePaymentResponse,
    StripePaymentTriggerRequest, StripePaymentTriggerResponse,
    StripeOrderRequest, StripeOrderResponse
)
from app.core import payment_handler
from app.core import led_handler
import stripe

router = APIRouter(prefix="/payments", tags=["payments"])


# ============================================================================
# STRIPE CUSTOMER ROUTES
# ============================================================================

@router.post("/stripe/customers", response_model=CustomerResponse)
def create_stripe_customer(customer_req: CustomerRequest):
    """Create a new Stripe customer"""
    try:
        result = payment_handler.create_customer(
            email=customer_req.email,
            name=customer_req.name
        )
        return CustomerResponse(**result)
    except stripe.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stripe/customers/{customer_id}", response_model=CustomerResponse)
def get_stripe_customer(customer_id: str):
    """Get Stripe customer details"""
    try:
        result = payment_handler.get_customer(customer_id)
        return CustomerResponse(**result)
    except stripe.StripeError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/stripe/customers/{customer_id}", response_model=CustomerResponse)
def update_stripe_customer(customer_id: str, customer_req: CustomerRequest):
    """Update Stripe customer"""
    try:
        result = payment_handler.update_customer(
            customer_id=customer_id,
            email=customer_req.email,
            name=customer_req.name
        )
        return CustomerResponse(**result)
    except stripe.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/stripe/customers/{customer_id}")
def delete_stripe_customer(customer_id: str):
    """Delete Stripe customer"""
    try:
        result = payment_handler.delete_customer(customer_id)
        return result
    except stripe.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# STRIPE PAYMENT ROUTES
# ============================================================================

@router.post("/stripe/payment", response_model=StripePaymentResponse)
def create_stripe_payment(payment_req: StripePaymentRequest):
    """Create a Stripe PaymentIntent"""
    try:
        result = payment_handler.create_payment(
            amount_cents=payment_req.amount_cents,
            customer_id=payment_req.customer_id,
            description=payment_req.description,
            metadata=payment_req.metadata
        )
        return StripePaymentResponse(**result)
    except stripe.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stripe/payment/{payment_intent_id}", response_model=StripePaymentResponse)
def get_stripe_payment(payment_intent_id: str):
    """Get PaymentIntent status"""
    try:
        result = payment_handler.get_payment(payment_intent_id)
        return StripePaymentResponse(**result)
    except stripe.StripeError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/stripe/payment/{payment_intent_id}/confirm", response_model=StripePaymentResponse)
def confirm_stripe_payment(payment_intent_id: str):
    """Confirm a PaymentIntent"""
    try:
        result = payment_handler.confirm_payment(payment_intent_id)
        return StripePaymentResponse(**result)
    except stripe.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stripe/payment/{payment_intent_id}/cancel", response_model=dict)
def cancel_stripe_payment(payment_intent_id: str):
    """Cancel a PaymentIntent"""
    try:
        result = payment_handler.cancel_payment(payment_intent_id)
        return result
    except stripe.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# STRIPE ORDER ROUTES
# ============================================================================

@router.post("/stripe/orders", response_model=StripeOrderResponse)
def create_stripe_order(
    order_req: StripeOrderRequest,
    cursor: RealDictCursor = Depends(get_db)
):
    """Create a new order in database"""
    try:
        result = payment_handler.create_order(
            cursor=cursor,
            customer_id=order_req.customer_id,
            hardware_id=order_req.hardware_id,
            service_type=order_req.service_type,
            amount_cents=order_req.amount_cents
        )
        return StripeOrderResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stripe/orders/{order_id}", response_model=StripeOrderResponse)
def get_stripe_order(order_id: str, cursor: RealDictCursor = Depends(get_db)):
    """Get order details"""
    result = payment_handler.get_order(cursor, order_id)
    if not result:
        raise HTTPException(status_code=404, detail="Order not found")
    return StripeOrderResponse(**result)


@router.put("/stripe/orders/{order_id}/status", response_model=StripeOrderResponse)
def update_stripe_order_status(
    order_id: str,
    status: str,
    cursor: RealDictCursor = Depends(get_db)
):
    """Update order status"""
    try:
        result = payment_handler.update_order_status(cursor, order_id, status)
        if not result:
            raise HTTPException(status_code=404, detail="Order not found")
        return StripeOrderResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stripe/customers/{customer_id}/orders")
def get_customer_stripe_orders(
    customer_id: str,
    cursor: RealDictCursor = Depends(get_db)
):
    """Get all orders for a customer"""
    try:
        results = payment_handler.get_customer_orders(cursor, customer_id)
        return [StripeOrderResponse(**order) for order in results]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# UNIFIED PAYMENT + LED TRIGGER ENDPOINT
# ============================================================================

@router.post("/stripe/payment-and-trigger", response_model=StripePaymentTriggerResponse)
async def create_payment_and_trigger_led(
    payment_req: StripePaymentTriggerRequest,
    cursor: RealDictCursor = Depends(get_db)
):
    """
    Create Stripe payment and trigger LED on Pi device via BLE

    Flow:
    1. Create PaymentIntent with Stripe
    2. Confirm payment (for test mode, use pm_card_visa)
    3. Based on payment status, trigger LED:
       - succeeded → green LED
       - failed/requires_action → red LED
    4. Return combined response
    """
    led_triggered = False
    led_color = "yellow"  # Default to processing

    try:
        # Step 1: Create PaymentIntent
        print(f"\n{'='*60}")
        print(f"[Payment+LED] STARTING PAYMENT FLOW")
        print(f"{'='*60}")
        print(f"[Payment+LED] Step 1: Creating Stripe PaymentIntent for ${payment_req.amount_cents/100:.2f} ({payment_req.amount_cents} cents)")
        print(f"[Payment+LED] Customer: {payment_req.customer_id or 'None (guest)'}")
        print(f"[Payment+LED] Device: {payment_req.device_id}")

        # Build payment intent params
        payment_params = {
            "amount": payment_req.amount_cents,
            "currency": "usd",
            "description": payment_req.description or f"Payment for device {payment_req.device_id}",
            "metadata": {
                "device_id": payment_req.device_id
            },
            "automatic_payment_methods": {
                "enabled": True,
                "allow_redirects": "never"  # No redirects for vending machine use case
            }
        }

        if payment_req.order_id:
            payment_params["metadata"]["order_id"] = payment_req.order_id

        # Only add customer if provided
        if payment_req.customer_id:
            payment_params["customer"] = payment_req.customer_id

        payment_intent = stripe.PaymentIntent.create(**payment_params)

        print(f"[Payment+LED] Step 2: PaymentIntent created successfully!")
        print(f"[Payment+LED] Payment ID: {payment_intent.id}")
        print(f"[Payment+LED] Status: {payment_intent.status}")

        # Step 2: For testing in sandbox, auto-confirm with test payment method
        # In production, client would confirm with actual card
        if payment_intent.status == "requires_payment_method":
            print(f"[Payment+LED] 💳 Step 3: Auto-confirming with test card 'pm_card_visa' (Stripe test mode)")
            payment_intent = stripe.PaymentIntent.confirm(
                payment_intent.id,
                payment_method="pm_card_visa"
            )
            print(f"[Payment+LED] Step 4: Payment confirmed!")
            print(f"[Payment+LED] Final status: {payment_intent.status}")

        # Step 3: Determine LED color based on payment status
        if payment_intent.status == "succeeded":
            led_color = "green"
        elif payment_intent.status in ["requires_action", "requires_confirmation"]:
            led_color = "yellow"
        else:
            led_color = "red"

        print(f"\n[Payment+LED] 🎨 LED Color Decision: {led_color.upper()} (based on status: {payment_intent.status})")
        print(f"[Payment+LED] 💡 Now triggering BLE LED on device {payment_req.device_id}...")
        print(f"{'='*60}")
        if payment_req.skip_led:
            print("[Payment+LED] ⚙️  Skip LED flag set — not triggering BLE for this request.")
            led_triggered = False
        else:
            led_success = await led_handler.trigger_led(
                color=led_color,
                duration=payment_req.duration_seconds
            )
            led_triggered = led_success

        print(f"{'='*60}")
        if led_triggered:
            print(f"[Payment+LED] SUCCESS! LED triggered successfully")
        else:
            print(f"[Payment+LED] LED trigger skipped or failed (expected without Pi hardware)")
        print(f"{'='*60}\n")

        # Step 5: Return response
        response = StripePaymentTriggerResponse(
            payment_intent_id=payment_intent.id,
            amount_cents=payment_intent.amount,
            payment_status=payment_intent.status,
            customer_id=payment_intent.customer if payment_intent.customer else None,
            led_triggered=led_triggered,
            led_color=led_color,
            led_device_id=payment_req.device_id,
            created_at=payment_intent.created
        )

        if payment_req.order_id and payment_intent.status == "succeeded":
            cursor.execute(
                """
                UPDATE orders
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                ("PAID", payment_req.order_id)
            )

        return response

    except stripe.StripeError as e:
        print(f"[Payment+LED] Stripe error: {e}")
        # Even if payment fails, try to trigger red LED
        try:
            await led_handler.trigger_led(color="red", duration=payment_req.duration_seconds)
            led_triggered = True
        except Exception as led_error:
            print(f"[Payment+LED] LED trigger also failed: {led_error}")

        if payment_req.order_id:
            cursor.execute(
                """
                UPDATE orders
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                ("FAILED", payment_req.order_id)
            )
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")

    except Exception as e:
        print(f"[Payment+LED] Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

