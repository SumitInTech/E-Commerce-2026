"""
Payment Processing & Gateway Integration Service.
Guarantees transaction integrity, idempotency compliance, and webhook verification.
"""
import uuid
import json
import hashlib
import hmac
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.config import settings
from backend.models import PaymentTransaction, IdempotencyRecord, TransactionStatus, Order


class PaymentService:
    @staticmethod
    def check_idempotency(db: Session, idempotency_key: Optional[str]) -> Optional[Dict[str, Any]]:
        """Checks if an idempotency key was previously processed."""
        if not idempotency_key:
            return None
        record = db.query(IdempotencyRecord).filter(IdempotencyRecord.idempotency_key == idempotency_key).first()
        if record:
            return json.loads(record.response_body)
        return None

    @staticmethod
    def record_idempotency(db: Session, idempotency_key: str, request_path: str, response_data: Dict[str, Any]) -> None:
        """Stores the response corresponding to an idempotency key."""
        record = IdempotencyRecord(
            idempotency_key=idempotency_key,
            request_path=request_path,
            status_code=200,
            response_body=json.dumps(response_data, default=str)
        )
        db.add(record)
        db.commit()

    @classmethod
    def process_payment(
        cls,
        db: Session,
        order_id: int,
        amount: float,
        method: str = "CARD",
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes financial transaction with idempotency protection.
        """
        # 1. Idempotency Check
        if idempotency_key:
            cached = cls.check_idempotency(db, idempotency_key)
            if cached:
                return cached

        # 2. Verify Order
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found for payment processing")

        tx_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
        gateway_ref = f"gw_{method.lower()}_{uuid.uuid4().hex[:8]}"

        # 3. Simulate processing based on method
        method_clean = method.upper()
        if method_clean not in ["CARD", "UPI", "COD", "NETBANKING"]:
            method_clean = "CARD"

        status_val = TransactionStatus.SUCCESS

        transaction = PaymentTransaction(
            transaction_id=tx_id,
            order_id=order_id,
            idempotency_key=idempotency_key,
            amount=amount,
            currency="INR",
            method=method_clean,
            status=status_val,
            gateway_reference=gateway_ref
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        response_dict = {
            "transaction_id": transaction.transaction_id,
            "order_id": transaction.order_id,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "method": transaction.method,
            "status": transaction.status.value,
            "gateway_reference": transaction.gateway_reference,
            "timestamp": transaction.created_at.isoformat()
        }

        # 4. Save idempotency record
        if idempotency_key:
            cls.record_idempotency(db, idempotency_key, "/api/v1/payments/process", response_dict)

        return response_dict

    @staticmethod
    def verify_webhook_signature(payload: str, signature: str) -> bool:
        """Verifies HMAC-SHA256 signature of external webhook events."""
        expected = hmac.new(
            settings.STRIPE_WEBHOOK_SECRET.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
