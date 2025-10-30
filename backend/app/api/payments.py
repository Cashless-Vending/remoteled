"""
Payment API endpoints (Mock implementation for development)
"""
from fastapi import APIRouter, Depends, HTTPException
from psycopg2.extras import RealDictCursor
from app.core.database import get_db
from app.core.config import settings
from app.models.schemas import (
    CustomerRequest, CustomerResponse,
    StripePaymentRequest, StripePaymentResponse,
    StripeOrderRequest, StripeOrderResponse
)
from app.core import payment_handler
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
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stripe/customers/{customer_id}", response_model=CustomerResponse)
def get_stripe_customer(customer_id: str):
    """Get Stripe customer details"""
    try:
        result = payment_handler.get_customer(customer_id)
        return CustomerResponse(**result)
    except stripe.error.StripeError as e:
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
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/stripe/customers/{customer_id}")
def delete_stripe_customer(customer_id: str):
    """Delete Stripe customer"""
    try:
        result = payment_handler.delete_customer(customer_id)
        return result
    except stripe.error.StripeError as e:
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
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stripe/payment/{payment_intent_id}", response_model=StripePaymentResponse)
def get_stripe_payment(payment_intent_id: str):
    """Get PaymentIntent status"""
    try:
        result = payment_handler.get_payment(payment_intent_id)
        return StripePaymentResponse(**result)
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/stripe/payment/{payment_intent_id}/confirm", response_model=StripePaymentResponse)
def confirm_stripe_payment(payment_intent_id: str):
    """Confirm a PaymentIntent"""
    try:
        result = payment_handler.confirm_payment(payment_intent_id)
        return StripePaymentResponse(**result)
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/stripe/payment/{payment_intent_id}/cancel", response_model=dict)
def cancel_stripe_payment(payment_intent_id: str):
    """Cancel a PaymentIntent"""
    try:
        result = payment_handler.cancel_payment(payment_intent_id)
        return result
    except stripe.error.StripeError as e:
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

