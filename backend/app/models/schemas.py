"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


# Enums matching database types
class ServiceType(str, Enum):
    TRIGGER = "TRIGGER"
    FIXED = "FIXED"
    VARIABLE = "VARIABLE"


class OrderStatus(str, Enum):
    CREATED = "CREATED"
    PAID = "PAID"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


class DeviceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"
    DEACTIVATED = "DEACTIVATED"


# Device Models
class DeviceResponse(BaseModel):
    id: str
    label: str
    model: Optional[str]
    location: Optional[str]
    status: DeviceStatus
    created_at: datetime


# Service/Product Models
class ServiceResponse(BaseModel):
    id: str
    device_id: str
    type: ServiceType
    price_cents: int
    fixed_minutes: Optional[int]
    minutes_per_25c: Optional[int]
    active: bool
    created_at: datetime
    
    @property
    def price_dollars(self) -> float:
        """Convert cents to dollars"""
        return self.price_cents / 100.0


class DeviceWithServicesResponse(BaseModel):
    device: DeviceResponse
    services: List[ServiceResponse]


# Order Models
class OrderCreateRequest(BaseModel):
    device_id: str
    product_id: str
    amount_cents: int


class OrderResponse(BaseModel):
    id: str
    device_id: str
    product_id: str
    amount_cents: int
    authorized_minutes: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime


class OrderStatusUpdateRequest(BaseModel):
    status: OrderStatus


# Authorization Models
class AuthorizationPayload(BaseModel):
    deviceId: str
    orderId: str
    type: ServiceType
    seconds: int
    nonce: str
    exp: int  # Unix timestamp


class AuthorizationResponse(BaseModel):
    id: str
    order_id: str
    device_id: str
    payload: AuthorizationPayload
    signature_hex: str
    expires_at: datetime
    created_at: datetime


class AuthorizationCreateRequest(BaseModel):
    order_id: str


# Telemetry/Log Models
class TelemetryEvent(str, Enum):
    STARTED = "STARTED"
    DONE = "DONE"
    ERROR = "ERROR"


class TelemetryRequest(BaseModel):
    event: TelemetryEvent
    order_id: Optional[str] = None
    details: Optional[str] = None
    payload_hash: Optional[str] = None


class LogResponse(BaseModel):
    id: str
    device_id: str
    direction: Literal["PI_TO_SRV", "SRV_TO_PI"]
    payload_hash: Optional[str]
    ok: bool
    details: Optional[str]
    created_at: datetime


# Payment Models
class PaymentIntentRequest(BaseModel):
    order_id: str
    amount_cents: int


class PaymentIntentResponse(BaseModel):
    order_id: str
    amount_cents: int
    payment_method: str
    status: str


class MockPaymentRequest(BaseModel):
    order_id: str
    success: bool = True


# Error Response
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int


# Health Check
class HealthCheckResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime

