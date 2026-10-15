"""
Customer Support & Admin Governance Database Entities.
Models SLA ticketing, vendor onboarding, and executive analytics.
"""
from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Float
from backend.database.base import Base


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False)
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Compatibility alias
    @property
    def description(self) -> str:
        return self.message

    @description.setter
    def description(self, value: str):
        self.message = value


class VendorApplication(Base):
    __tablename__ = "vendor_applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    store_name = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=True)
    business_registration = Column(String(100), nullable=True)
    category = Column(String(100), default="Men's Apparel")
    status = Column(String(50), default="pending")  # pending, approved, rejected
    commission_rate = Column(Float, default=0.15)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Compatibility alias
    @property
    def brand_name(self) -> str:
        return self.store_name

    @brand_name.setter
    def brand_name(self, value: str):
        self.store_name = value

    @property
    def business_reg_no(self) -> str:
        return self.business_registration or ""

    @business_reg_no.setter
    def business_reg_no(self, value: str):
        self.business_registration = value

    @property
    def submitted_at(self) -> datetime:
        return self.created_at
