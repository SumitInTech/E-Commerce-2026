"""
Customer Support & Admin Governance Service.
Powers operator ticket workflows, vendor onboarding, and operational governance metrics.
"""
import random
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException

from backend.models import (
    SupportTicket, VendorApplication, TicketStatus, TicketPriority,
    Order, Product, User, UserRole, OrderStatus
)
from backend.schemas.admin import TicketCreateRequest, VendorApplyRequest, PlatformMetricsResponse


class AdminService:
    # -------------------------------------------------------------
    # Support Ticketing
    # -------------------------------------------------------------
    @staticmethod
    def create_ticket(db: Session, req: TicketCreateRequest, user_id: Optional[int] = None) -> SupportTicket:
        t_num = f"TCK-{random.randint(1000, 9999)}"
        p_enum = TicketPriority(req.priority.lower()) if req.priority else TicketPriority.MEDIUM
        ticket = SupportTicket(
            ticket_number=t_num,
            user_id=user_id,
            customer_name=req.customer_name,
            customer_email=req.customer_email,
            subject=req.subject,
            message=req.message,
            priority=p_enum,
            status=TicketStatus.OPEN
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def list_tickets(db: Session, status: Optional[str] = None) -> List[SupportTicket]:
        q = db.query(SupportTicket)
        if status:
            try:
                q = q.filter(SupportTicket.status == TicketStatus(status.lower()))
            except ValueError:
                pass
        return q.order_by(SupportTicket.id.desc()).all()

    @staticmethod
    def update_ticket(db: Session, ticket_id: int, new_status: Optional[str] = None, admin_notes: Optional[str] = None) -> SupportTicket:
        t = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
        if not t:
            raise HTTPException(status_code=404, detail="Ticket not found")

        if new_status:
            try:
                t.status = TicketStatus(new_status.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid ticket status: {new_status}")

        if admin_notes is not None:
            t.admin_notes = admin_notes

        db.commit()
        db.refresh(t)
        return t

    # -------------------------------------------------------------
    # Vendor Onboarding
    # -------------------------------------------------------------
    @staticmethod
    def apply_vendor(db: Session, req: VendorApplyRequest, user_id: Optional[int] = None) -> VendorApplication:
        app = VendorApplication(
            user_id=user_id,
            store_name=req.store_name,
            contact_name=req.contact_name,
            contact_email=req.contact_email,
            contact_phone=req.contact_phone,
            business_registration=req.business_registration,
            category=req.category,
            status="pending",
            commission_rate=0.15
        )
        db.add(app)
        db.commit()
        db.refresh(app)
        return app

    @staticmethod
    def list_vendor_applications(db: Session) -> List[VendorApplication]:
        return db.query(VendorApplication).order_by(VendorApplication.id.desc()).all()

    @staticmethod
    def update_vendor_status(db: Session, app_id: int, new_status: str) -> VendorApplication:
        app = db.query(VendorApplication).filter(VendorApplication.id == app_id).first()
        if not app:
            raise HTTPException(status_code=404, detail="Vendor application not found")

        app.status = new_status.lower()
        if app.status == "approved" and app.user_id:
            user = db.query(User).filter(User.id == app.user_id).first()
            if user:
                user.role = UserRole.SELLER

        db.commit()
        db.refresh(app)
        return app

    # -------------------------------------------------------------
    # Operational Governance Metrics
    # -------------------------------------------------------------
    @staticmethod
    def get_platform_metrics(db: Session) -> PlatformMetricsResponse:
        total_sales = db.query(func.sum(Order.total_amount)).scalar() or 0.0
        order_count = db.query(Order).count()
        prod_count = db.query(Product).count()
        cust_count = db.query(User).filter(User.role == UserRole.BUYER).count()
        open_tickets = db.query(SupportTicket).filter(SupportTicket.status == TicketStatus.OPEN).count()
        pending_vendors = db.query(VendorApplication).filter(VendorApplication.status == "pending").count()
        aov = round(total_sales / order_count, 2) if order_count > 0 else 0.0

        return PlatformMetricsResponse(
            total_sales_revenue=round(float(total_sales), 2),
            total_orders_count=order_count,
            total_products_count=prod_count,
            total_customers_count=cust_count,
            open_tickets_count=open_tickets,
            pending_vendor_applications=pending_vendors,
            average_order_value=aov,
            system_health="OPTIMAL"
        )
