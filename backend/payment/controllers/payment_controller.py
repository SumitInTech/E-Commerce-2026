"""
Payment HTTP Controller.
Parses idempotency tokens, coordinates payment lifecycle, and formats responses.
"""
from typing import Optional
from fastapi import HTTPException, status, Header
from sqlalchemy.orm import Session

from backend.payment.services.payment_service import payment_service
from backend.payment.schemas.payment_schema import (
    PaymentProcessRequest,
    PaymentResponse,
    RefundRequest
)


class PaymentController:
    @staticmethod
    def process_payment(
        db: Session,
        req: PaymentProcessRequest,
        idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")
    ) -> PaymentResponse:
        tx, message = payment_service.process_payment(db, req, idempotency_key=idempotency_key)

        response = PaymentResponse(
            transaction_id=tx.id,
            order_id=tx.order_id,
            amount=tx.amount,
            currency=tx.currency,
            status=tx.status,
            payment_method=tx.payment_method,
            gateway_tx_id=tx.gateway_tx_id,
            created_at=tx.created_at,
            message=message
        )

        # Store in idempotency cache only on first non-cached execution
        if idempotency_key and message != "Replayed from idempotency cache":
            if not payment_service.check_idempotency(db, idempotency_key):
                payment_service.record_idempotency(
                    db=db,
                    key=idempotency_key,
                    path="/api/v1/payments/process",
                    status_code=200,
                    payload=response.model_dump(mode="json")
                )

        return response

    @staticmethod
    def refund(db: Session, req: RefundRequest) -> PaymentResponse:
        try:
            tx = payment_service.refund_transaction(db, req.transaction_id, req.reason)
            return PaymentResponse(
                transaction_id=tx.id,
                order_id=tx.order_id,
                amount=tx.amount,
                currency=tx.currency,
                status=tx.status,
                payment_method=tx.payment_method,
                gateway_tx_id=tx.gateway_tx_id,
                created_at=tx.created_at,
                message=f"Refund processed: {req.reason}"
            )
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    def get_transaction(db: Session, tx_id: int) -> PaymentResponse:
        tx = payment_service.get_transaction(db, tx_id)
        if not tx:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        return PaymentResponse(
            transaction_id=tx.id,
            order_id=tx.order_id,
            amount=tx.amount,
            currency=tx.currency,
            status=tx.status,
            payment_method=tx.payment_method,
            gateway_tx_id=tx.gateway_tx_id,
            created_at=tx.created_at,
            message="Transaction retrieved"
        )


payment_controller = PaymentController()
