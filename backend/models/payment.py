"""
Payment Transaction & Idempotency Database Models.
"""
from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from backend.models.user import Base


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
    created_at = Column(DateTime, default=datetime.utcnow)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"

    id = Column(Integer, primary_key=True, index=True)
    idempotency_key = Column(String(100), unique=True, index=True, nullable=False)
    request_path = Column(String(255), nullable=False)
    status_code = Column(Integer, default=200)
    response_body = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
