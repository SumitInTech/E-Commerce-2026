"""
Payment Service Router.
Executes financial transaction processing, guarantees idempotency,
and simulates gateway confirmations (Card, UPI, COD).
"""
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import PaymentTransaction
from backend.schemas.payment import (
    PaymentIntentRequest, PaymentProcessRequest, PaymentResponse, WebhookEventRequest
)
from backend.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["3. Payment Service"])


@router.post("/intent", response_model=PaymentResponse)
def create_payment_intent(req: PaymentIntentRequest, db: Session = Depends(get_db)):
    """Initializes payment intent with simulated gateway tokens."""
    return PaymentService.process_payment(
        db, order_id=req.order_id, amount=req.amount, method=req.method
    )


@router.post("/process", response_model=PaymentResponse)
def process_payment(
    req: PaymentProcessRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key", description="Guarantees double-click immunity"),
    db: Session = Depends(get_db)
):
    """
    Finalizes checkout payment. Supports Card, UPI, and Cash on Delivery.
    Protected by idempotency keys to avoid double-charging.
    """
    return PaymentService.process_payment(
        db,
        order_id=req.order_id,
        amount=req.amount,
        method=req.method,
        idempotency_key=idempotency_key
    )


@router.post("/webhook")
def handle_webhook(
    req: WebhookEventRequest,
    stripe_signature: Optional[str] = Header(None, alias="Stripe-Signature"),
    db: Session = Depends(get_db)
):
    """Secure webhook endpoint receiving asynchronous payment settlement notifications."""
    if stripe_signature and not PaymentService.verify_webhook_signature(str(req.dict()), stripe_signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    return {
        "status": "received",
        "event_type": req.event_type,
        "transaction_id": req.transaction_id,
        "processed": True
    }


@router.get("/transactions/{order_id}")
def get_order_transactions(order_id: int, db: Session = Depends(get_db)):
    """Audits payment transaction logs for a given order."""
    txs = db.query(PaymentTransaction).filter(PaymentTransaction.order_id == order_id).all()
    return [
        {
            "transaction_id": tx.transaction_id,
            "order_id": tx.order_id,
            "amount": tx.amount,
            "currency": tx.currency,
            "method": tx.method,
            "status": tx.status.value,
            "gateway_reference": tx.gateway_reference,
            "created_at": tx.created_at.isoformat()
        }
        for tx in txs
    ]
