"""
Customer Support & Admin Governance HTTP Controller.
Coordinates support triage, vendor approvals, and operational dashboards.
"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.customer_admin.services.admin_service import admin_service
from backend.customer_admin.models.admin_model import TicketStatus
from backend.customer_admin.schemas.admin_schema import (
    TicketCreateRequest,
    TicketResponse,
    TicketUpdateRequest,
    VendorApplyRequest,
    VendorResponse,
    AdminMetricsResponse
)


class AdminController:
    @staticmethod
    def create_ticket(db: Session, req: TicketCreateRequest) -> TicketResponse:
        ticket = admin_service.create_ticket(db, req)
        return TicketResponse.model_validate(ticket)

    @staticmethod
    def list_tickets(db: Session, status_filter: Optional[TicketStatus] = None, limit: int = 50) -> List[TicketResponse]:
        tickets = admin_service.get_tickets(db, status_filter=status_filter, limit=limit)
        return [TicketResponse.model_validate(t) for t in tickets]

    @staticmethod
    def update_ticket(db: Session, ticket_id: int, req: TicketUpdateRequest) -> TicketResponse:
        try:
            ticket = admin_service.update_ticket_status(db, ticket_id, req.status)
            return TicketResponse.model_validate(ticket)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    @staticmethod
    def list_vendors(db: Session, limit: int = 50) -> List[VendorResponse]:
        apps = admin_service.list_vendors(db, limit=limit)
        return [VendorResponse.model_validate(a) for a in apps]

    @staticmethod
    def apply_vendor(db: Session, req: VendorApplyRequest) -> VendorResponse:
        try:
            app = admin_service.apply_vendor(db, req)
            return VendorResponse.model_validate(app)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    def approve_vendor(db: Session, application_id: int) -> VendorResponse:
        try:
            app = admin_service.approve_vendor(db, application_id)
            return VendorResponse.model_validate(app)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    @staticmethod
    def get_metrics(db: Session) -> AdminMetricsResponse:
        metrics = admin_service.get_metrics(db)
        return AdminMetricsResponse(**metrics)


admin_controller = AdminController()
