"""
Customer & Admin Service Router.
Powers customer support inquiries, vendor onboarding, and executive business analytics.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.schemas.admin import (
    TicketCreateRequest, TicketResponse, TicketUpdateRequest,
    VendorApplyRequest, PlatformMetricsResponse
)
from backend.services.admin_service import AdminService
from backend.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/admin", tags=["5. Customer & Admin Service"])


@router.get("/metrics", response_model=PlatformMetricsResponse)
def get_metrics(
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calculates live platform Gross Merchandise Value (GMV), ticket loads, and catalog stats."""
    return AdminService.get_platform_metrics(db)


@router.post("/tickets", response_model=TicketResponse)
def create_ticket(
    req: TicketCreateRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Customer-facing endpoint to submit sizing questions or return requests."""
    user_id = current_user.id if current_user else None
    return AdminService.create_ticket(db, req, user_id=user_id)


@router.get("/tickets", response_model=List[TicketResponse])
def list_tickets(
    status: Optional[str] = Query(None, description="open, in_progress, resolved, closed"),
    db: Session = Depends(get_db)
):
    """Lists customer support tickets for administrative triage."""
    return AdminService.list_tickets(db, status=status)


@router.patch("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    req: TicketUpdateRequest,
    db: Session = Depends(get_db)
):
    """Updates ticket status and writes operator response notes."""
    return AdminService.update_ticket(db, ticket_id, new_status=req.status, admin_notes=req.admin_notes)


@router.post("/vendors/apply")
def apply_vendor(
    req: VendorApplyRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enables streetwear brands to apply for vendor marketplace onboarding."""
    user_id = current_user.id if current_user else None
    app = AdminService.apply_vendor(db, req, user_id=user_id)
    return {
        "status": "submitted",
        "application_id": app.id,
        "store_name": app.store_name,
        "message": "Vendor application received. Review usually takes 2 business days."
    }


@router.get("/vendors")
def list_vendors(
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists vendor onboarding applications."""
    return AdminService.list_vendor_applications(db)


@router.patch("/vendors/{app_id}/status")
def update_vendor_status(
    app_id: int,
    status: str = Query(..., description="approved or rejected"),
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db)
):
    """Admin-only endpoint to approve or reject vendor marketplace applications."""
    return AdminService.update_vendor_status(db, app_id, status)
