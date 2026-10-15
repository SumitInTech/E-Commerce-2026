"""
Payment Database Entities for Financial Isolation & Idempotency.
Guarantees transaction integrity and prevents duplicate charges.
"""
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, Text, ForeignKey
from backend.database.base import Base


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(100), unique=True, index=True, nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    idempotency_key = Column(String(100), index=True, nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    method = Column(String(50), default="CARD")  # CARD, UPI, COD, NETBANKING
    status = Column(Enum(TransactionStatus), default=TransactionStatus.SUCCESS, nullable=False)
    gateway_reference = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Compatibility aliases
    @property
    def payment_method(self) -> str:
        return self.method

    @payment_method.setter
    def payment_method(self, value: str):
        self.method = value

    @property
    def gateway_tx_id(self) -> str:
        return self.gateway_reference or self.transaction_id


class IdempotencyRecord(Base):
    """Stores client idempotency keys to prevent duplicate payments on retry."""
    __tablename__ = "idempotency_records"

    id = Column(Integer, primary_key=True, index=True)
    idempotency_key = Column(String(100), unique=True, index=True, nullable=False)
    request_path = Column(String(255), nullable=False)
    status_code = Column(Integer, default=200)
    response_body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Compatibility alias
    @property
    def response_payload(self) -> str:
        return self.response_body
