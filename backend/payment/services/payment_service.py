"""
Payment Business Domain Service.
Implements Idempotency checks, gateway routing, and atomic financial status transitions.
"""
import uuid
import json
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from backend.payment.models.payment_model import PaymentTransaction, IdempotencyRecord, TransactionStatus
from backend.payment.schemas.payment_schema import PaymentProcessRequest


class PaymentService:
    @staticmethod
    def check_idempotency(db: Session, key: str) -> Optional[IdempotencyRecord]:
        """Checks if an idempotency key was previously processed."""
        if not key:
            return None
        return db.query(IdempotencyRecord).filter(IdempotencyRecord.idempotency_key == key).first()

    @staticmethod
    def record_idempotency(db: Session, key: str, path: str, status_code: int, payload: dict) -> None:
        """Stores idempotency record to guarantee single execution."""
        record = IdempotencyRecord(
            idempotency_key=key,
            request_path=path,
            status_code=status_code,
            response_body=json.dumps(payload)
        )
        db.add(record)
        db.commit()

    @classmethod
    def process_payment(
        cls,
        db: Session,
        req: PaymentProcessRequest,
        idempotency_key: Optional[str] = None
    ) -> Tuple[PaymentTransaction, str]:
        """
        Processes financial transaction.
        Simulates payment gateway integration (Razorpay / Stripe / UPI).
        """
        # Idempotency check
        if idempotency_key:
            existing = cls.check_idempotency(db, idempotency_key)
            if existing:
                tx = db.query(PaymentTransaction).filter(
                    PaymentTransaction.idempotency_key == idempotency_key
                ).first()
                if tx:
                    return tx, "Replayed from idempotency cache"

        # Gateway simulation
        gateway_tx_id = f"tx_live_{uuid.uuid4().hex[:16]}"
        is_success = True
        status_value = TransactionStatus.SUCCESS if is_success else TransactionStatus.FAILED
        message = "Payment completed successfully via gateway"

        tx = PaymentTransaction(
            transaction_id=gateway_tx_id,
            order_id=req.order_id,
            amount=req.amount,
            currency=req.currency or "INR",
            status=status_value,
            method=req.payment_method.upper(),
            gateway_reference=gateway_tx_id,
            idempotency_key=idempotency_key
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)

        # Update order status if order exists
        try:
            from backend.order.models.order_model import Order, OrderStatus
            order = db.query(Order).filter(Order.id == req.order_id).first()
            if order and is_success:
                order.status = OrderStatus.CONFIRMED
                db.commit()
        except Exception:
            pass

        return tx, message

    @staticmethod
    def refund_transaction(db: Session, transaction_id: int, reason: str) -> PaymentTransaction:
        tx = db.query(PaymentTransaction).filter(PaymentTransaction.id == transaction_id).first()
        if not tx:
            raise ValueError(f"Transaction ID {transaction_id} not found")
        if tx.status != TransactionStatus.SUCCESS:
            raise ValueError(f"Cannot refund transaction in status {tx.status}")

        tx.status = TransactionStatus.REFUNDED
        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def get_transaction(db: Session, tx_id: int) -> Optional[PaymentTransaction]:
        return db.query(PaymentTransaction).filter(PaymentTransaction.id == tx_id).first()


payment_service = PaymentService()
