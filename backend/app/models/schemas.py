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


# Service Models (Global services)
class ServiceResponse(BaseModel):
    id: str
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
    service_id: str
    amount_cents: int


class OrderResponse(BaseModel):
    id: str
    device_id: str
    service_id: str
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
    order_id: Optional[str]
    details: Optional[str]
    payload_hash: Optional[str]


class LogResponse(BaseModel):
    id: str
    device_id: str
    direction: Literal["PI_TO_SRV", "SRV_TO_PI"]
    payload_hash: Optional[str]
    ok: bool
    details: Optional[str]
    created_at: datetime


# Stripe Payment Models
class CustomerRequest(BaseModel):
    email: str
    name: str


class CustomerResponse(BaseModel):
    customer_id: str
    email: str
    name: str
    created_at: int  # Unix timestamp from Stripe


class StripePaymentRequest(BaseModel):
    amount_cents: int
    customer_id: str
    description: Optional[str] = None
    metadata: Optional[dict] = None


class StripePaymentResponse(BaseModel):
    payment_intent_id: str
    amount_cents: int
    status: str
    customer_id: str
    created_at: int  # Unix timestamp


class StripePaymentTriggerRequest(BaseModel):
    amount_cents: int
    customer_id: Optional[str] = None  # Optional for testing
    device_id: str  # Which Pi device to trigger LED on
    description: Optional[str] = None
    duration_seconds: Optional[int] = 3  # How long to keep LED on
    order_id: Optional[str] = None  # Associated order (optional)
    skip_led: Optional[bool] = False  # Allow skipping BLE during tests


class StripePaymentTriggerResponse(BaseModel):
    payment_intent_id: str
    amount_cents: int
    payment_status: str
    customer_id: Optional[str]
    led_triggered: bool
    led_color: str
    led_device_id: str
    created_at: int  # Unix timestamp


class StripeOrderRequest(BaseModel):
    customer_id: str
    hardware_id: str
    service_type: str
    amount_cents: int


class StripeOrderResponse(BaseModel):
    order_id: str
    customer_id: str
    hardware_id: str
    service_type: str
    amount_cents: int
    payment_intent_id: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime


# Error Response
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int


# Device-Service Assignment Models
class DeviceServiceAssignmentRequest(BaseModel):
    device_id: str
    service_id: str


class DeviceServiceAssignmentResponse(BaseModel):
    id: str
    device_id: str
    service_id: str
    created_at: datetime


# Reference Data Models

# Device Model Reference
class DeviceModelBase(BaseModel):
    name: str
    description: Optional[str] = None


class DeviceModelCreate(DeviceModelBase):
    pass


class DeviceModelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class DeviceModelResponse(DeviceModelBase):
    id: str
    created_at: datetime


# Location Reference
class LocationBase(BaseModel):
    name: str
    description: Optional[str] = None


class LocationCreate(LocationBase):
    pass


class LocationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class LocationResponse(LocationBase):
    id: str
    created_at: datetime


# Service Type Reference (Read-only, maps to ENUM)
class ServiceTypeCreate(BaseModel):
    name: str
    code: str
    description: Optional[str] = None


class ServiceTypeUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None


class ServiceTypeResponse(BaseModel):
    id: str
    name: str
    code: ServiceType
    description: Optional[str] = None
    created_at: datetime


# Health Check
class HealthCheckResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime

