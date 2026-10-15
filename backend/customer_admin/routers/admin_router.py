"""
Customer Support & Admin Governance API Router.
Registers HTTP endpoints for ticketing, vendor onboarding, and executive analytics.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.supabase_client import get_db
from backend.customer_admin.schemas.admin_schema import (
    TicketCreateRequest,
    TicketResponse,
    TicketUpdateRequest,
    VendorApplyRequest,
    VendorResponse,
    AdminMetricsResponse
)
from backend.customer_admin.models.admin_model import TicketStatus
from backend.customer_admin.controllers.admin_controller import admin_controller

router = APIRouter(prefix="/admin", tags=["Customer & Admin Service"])


@router.get("/metrics", response_model=AdminMetricsResponse)
def get_metrics(db: Session = Depends(get_db)):
    """Retrieves high-level platform GMV, order counts, and AI return-rate mitigation metrics."""
    return admin_controller.get_metrics(db)


@router.post("/tickets", response_model=TicketResponse)
def create_ticket(req: TicketCreateRequest, db: Session = Depends(get_db)):
    """Submits a customer support or sizing dispute ticket."""
    return admin_controller.create_ticket(db, req)


@router.get("/tickets", response_model=List[TicketResponse])
def list_tickets(status: Optional[TicketStatus] = None, limit: int = 50, db: Session = Depends(get_db)):
    """Retrieves support ticket queue with status filtering."""
    return admin_controller.list_tickets(db, status_filter=status, limit=limit)


@router.patch("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(ticket_id: int, req: TicketUpdateRequest, db: Session = Depends(get_db)):
    """Updates support ticket status (e.g. IN_PROGRESS -> RESOLVED)."""
    return admin_controller.update_ticket(db, ticket_id, req)


@router.get("/vendors", response_model=List[VendorResponse])
def list_vendors(limit: int = 50, db: Session = Depends(get_db)):
    """Retrieves all registered vendor applications."""
    return admin_controller.list_vendors(db, limit=limit)


@router.post("/vendors", response_model=VendorResponse)
def apply_vendor(req: VendorApplyRequest, db: Session = Depends(get_db)):
    """Submits a merchant/seller onboarding application."""
    return admin_controller.apply_vendor(db, req)


@router.post("/vendors/apply", response_model=VendorResponse)
def apply_vendor_alias(req: VendorApplyRequest, db: Session = Depends(get_db)):
    """Alias for merchant onboarding application."""
    return admin_controller.apply_vendor(db, req)


@router.patch("/vendors/{application_id}/approve", response_model=VendorResponse)
def approve_vendor(application_id: int, db: Session = Depends(get_db)):
    """Approves a vendor application and elevates user to SELLER role."""
    return admin_controller.approve_vendor(db, application_id)
