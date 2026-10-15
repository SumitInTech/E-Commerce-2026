"""
Payment API Router.
Registers HTTP endpoints for payments processing, verification, and refunds.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from backend.database.supabase_client import get_db
from backend.payment.schemas.payment_schema import (
    PaymentProcessRequest,
    PaymentResponse,
    RefundRequest
)
from backend.payment.controllers.payment_controller import payment_controller

router = APIRouter(prefix="/payments", tags=["Payment Service"])


@router.post("/process", response_model=PaymentResponse)
def process_payment(
    req: PaymentProcessRequest,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: Session = Depends(get_db)
):
    """Processes financial transaction with strict idempotency key protection."""
    return payment_controller.process_payment(db, req, idempotency_key=idempotency_key)


@router.get("/transaction/{tx_id}", response_model=PaymentResponse)
def get_transaction(tx_id: int, db: Session = Depends(get_db)):
    """Retrieves payment transaction audit status."""
    return payment_controller.get_transaction(db, tx_id)


@router.post("/refund", response_model=PaymentResponse)
def refund_payment(req: RefundRequest, db: Session = Depends(get_db)):
    """Initiates financial refund for an eligible transaction."""
    return payment_controller.refund(db, req)
