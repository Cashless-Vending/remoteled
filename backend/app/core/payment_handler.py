"""
Stripe payment handler with CRUD operations
"""
import stripe
from datetime import datetime
from typing import Optional, List, Dict, Any
from psycopg2.extras import RealDictCursor
from app.core.config import settings


# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


# ============================================================================
# CUSTOMER CRUD
# ============================================================================

def create_customer(email: str, name: str) -> Dict[str, Any]:
    """Create a Stripe customer"""
    customer = stripe.Customer.create(
        email=email,
        name=name
    )
    return {
        "customer_id": customer.id,
        "email": customer.email,
        "name": customer.name,
        "created_at": customer.created
    }


def get_customer(customer_id: str) -> Dict[str, Any]:
    """Get Stripe customer details"""
    customer = stripe.Customer.retrieve(customer_id)
    return {
        "customer_id": customer.id,
        "email": customer.email,
        "name": customer.name,
        "created_at": customer.created
    }


def update_customer(customer_id: str, email: Optional[str] = None, name: Optional[str] = None) -> Dict[str, Any]:
    """Update Stripe customer"""
    update_data = {}
    if email:
        update_data["email"] = email
    if name:
        update_data["name"] = name

    customer = stripe.Customer.modify(customer_id, **update_data)
    return {
        "customer_id": customer.id,
        "email": customer.email,
        "name": customer.name,
        "created_at": customer.created
    }


def delete_customer(customer_id: str) -> Dict[str, Any]:
    """Delete Stripe customer"""
    result = stripe.Customer.delete(customer_id)
    return {
        "customer_id": result.id,
        "deleted": result.deleted
    }


# ============================================================================
# PAYMENT CRUD
# ============================================================================

def create_payment(
    amount_cents: int,
    customer_id: str,
    description: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> Dict[str, Any]:
    """Create a Stripe PaymentIntent"""
    payment_intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency="usd",
        customer=customer_id,
        description=description,
        metadata=metadata or {},
        automatic_payment_methods={"enabled": True}
    )
    return {
        "payment_intent_id": payment_intent.id,
        "amount_cents": payment_intent.amount,
        "status": payment_intent.status,
        "customer_id": payment_intent.customer,
        "created_at": payment_intent.created
    }


def get_payment(payment_intent_id: str) -> Dict[str, Any]:
    """Get PaymentIntent status"""
    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    return {
        "payment_intent_id": payment_intent.id,
        "amount_cents": payment_intent.amount,
        "status": payment_intent.status,
        "customer_id": payment_intent.customer,
        "created_at": payment_intent.created
    }


def confirm_payment(payment_intent_id: str) -> Dict[str, Any]:
    """Confirm a PaymentIntent"""
    payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)
    return {
        "payment_intent_id": payment_intent.id,
        "amount_cents": payment_intent.amount,
        "status": payment_intent.status,
        "customer_id": payment_intent.customer,
        "created_at": payment_intent.created
    }


def cancel_payment(payment_intent_id: str) -> Dict[str, Any]:
    """Cancel a PaymentIntent"""
    payment_intent = stripe.PaymentIntent.cancel(payment_intent_id)
    return {
        "payment_intent_id": payment_intent.id,
        "status": payment_intent.status
    }


# ============================================================================
# ORDER CRUD (Database)
# ============================================================================

def create_order(
    cursor: RealDictCursor,
    customer_id: str,
    hardware_id: str,
    service_type: str,
    amount_cents: int,
    payment_intent_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create an order in database"""
    cursor.execute(
        """
        INSERT INTO stripe_orders (customer_id, hardware_id, service_type, amount_cents, payment_intent_id, status)
        VALUES (%s, %s, %s, %s, %s, 'CREATED')
        RETURNING id, customer_id, hardware_id, service_type, amount_cents, payment_intent_id, status, created_at, updated_at
        """,
        (customer_id, hardware_id, service_type, amount_cents, payment_intent_id)
    )
    return cursor.fetchone()


def get_order(cursor: RealDictCursor, order_id: str) -> Optional[Dict[str, Any]]:
    """Get order from database"""
    cursor.execute(
        """
        SELECT id, customer_id, hardware_id, service_type, amount_cents, payment_intent_id, status, created_at, updated_at
        FROM stripe_orders
        WHERE id = %s
        """,
        (order_id,)
    )
    return cursor.fetchone()


def update_order_status(cursor: RealDictCursor, order_id: str, status: str) -> Dict[str, Any]:
    """Update order status"""
    cursor.execute(
        """
        UPDATE stripe_orders
        SET status = %s, updated_at = NOW()
        WHERE id = %s
        RETURNING id, customer_id, hardware_id, service_type, amount_cents, payment_intent_id, status, created_at, updated_at
        """,
        (status, order_id)
    )
    return cursor.fetchone()


def get_customer_orders(cursor: RealDictCursor, customer_id: str) -> List[Dict[str, Any]]:
    """Get all orders for a customer"""
    cursor.execute(
        """
        SELECT id, customer_id, hardware_id, service_type, amount_cents, payment_intent_id, status, created_at, updated_at
        FROM stripe_orders
        WHERE customer_id = %s
        ORDER BY created_at DESC
        """,
        (customer_id,)
    )
    return cursor.fetchall()
