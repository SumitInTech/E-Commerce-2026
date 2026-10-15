"""
Pydantic v2 Schemas for Payment Processing & Gateway Integrations.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from backend.payment.models.payment_model import TransactionStatus


class PaymentProcessRequest(BaseModel):
    order_id: int
    user_id: Optional[int] = 1
    amount: float = Field(..., gt=0)
    payment_method: Optional[str] = Field(default=None, description="'card', 'upi', or 'cod'")
    method: Optional[str] = Field(default="CARD", description="Legacy alias for payment_method")
    currency: Optional[str] = "INR"
    card_token: Optional[str] = None
    upi_id: Optional[str] = None

    def model_post_init(self, __context):
        if not self.payment_method and self.method:
            self.payment_method = self.method


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: int
    order_id: int
    amount: float
    currency: str
    status: TransactionStatus
    payment_method: str
    gateway_tx_id: Optional[str] = None
    created_at: datetime
    message: str


class RefundRequest(BaseModel):
    transaction_id: int
    reason: str
    amount: Optional[float] = None
