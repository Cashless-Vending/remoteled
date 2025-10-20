from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

class PaymentRequest(BaseModel):
    amount: float
    service: str = "basic"

class PaymentResponse(BaseModel):
    status: str  # "success", "fail", "processing"
    led_color: str  # "green", "red", "yellow"
    duration: int  # seconds
    message: str

@app.post("/payment", response_model=PaymentResponse)
async def process_payment(payment: PaymentRequest):
    """
    Fake payment endpoint for testing.
    Returns random status to simulate real payment processing.

    Status → LED mapping:
    - success → green LED
    - fail → red LED
    - processing → yellow LED
    """

    # Fake payment logic - randomly assign status
    statuses = ["success", "fail", "processing"]
    weights = [0.7, 0.2, 0.1]  # 70% success, 20% fail, 10% processing
    status = random.choices(statuses, weights=weights)[0]

    # Map status to LED color
    led_mapping = {
        "success": "green",
        "fail": "red",
        "processing": "yellow"
    }

    led_color = led_mapping[status]

    # Duration based on service type
    duration = 30 if payment.service == "premium" else 10

    return PaymentResponse(
        status=status,
        led_color=led_color,
        duration=duration,
        message=f"Payment {status} - Amount: ${payment.amount}"
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}
