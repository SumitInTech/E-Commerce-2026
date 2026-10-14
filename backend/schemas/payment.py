"""
Payment Processing & Gateway Schemas.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PaymentIntentRequest(BaseModel):
    order_id: int
    amount: float
    currency: str = "INR"
    method: str = "CARD"  # CARD, UPI, COD, NETBANKING


class PaymentProcessRequest(BaseModel):
    order_id: int
    amount: float
    method: str = "CARD"
    card_number: Optional[str] = "4242••••••••4242"
    upi_id: Optional[str] = None


class PaymentResponse(BaseModel):
    transaction_id: str
    order_id: int
    amount: float
    currency: str
    method: str
    status: str
    gateway_reference: str
    timestamp: datetime


class WebhookEventRequest(BaseModel):
    event_type: str  # payment.succeeded, payment.failed, charge.refunded
    order_id: int
    transaction_id: str
    amount: float
    signature: str
