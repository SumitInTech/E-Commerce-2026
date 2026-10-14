"""
Admin, Support & Governance Schemas.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class TicketCreateRequest(BaseModel):
    customer_name: str
    customer_email: str
    subject: str
    message: str
    priority: Optional[str] = "medium"


class TicketUpdateRequest(BaseModel):
    status: Optional[str] = None
    admin_notes: Optional[str] = None


class TicketResponse(BaseModel):
    id: int
    ticket_number: str
    customer_name: str
    customer_email: str
    subject: str
    message: str
    priority: str
    status: str
    admin_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VendorApplyRequest(BaseModel):
    store_name: str
    contact_name: str
    contact_email: str
    contact_phone: Optional[str] = None
    business_registration: Optional[str] = None
    category: Optional[str] = "Men's Streetwear"


class PlatformMetricsResponse(BaseModel):
    total_sales_revenue: float
    total_orders_count: int
    total_products_count: int
    total_customers_count: int
    open_tickets_count: int
    pending_vendor_applications: int
    average_order_value: float
    system_health: str
