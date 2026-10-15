"""
Pydantic v2 Schemas for Support Tickets, Vendor Onboarding & Platform Metrics.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from backend.customer_admin.models.admin_model import TicketStatus, TicketPriority


class TicketCreateRequest(BaseModel):
    user_id: Optional[int] = 1
    order_id: Optional[int] = None
    customer_name: Optional[str] = "Valued Buyer"
    customer_email: Optional[str] = "buyer@snitch.com"
    subject: str = Field(..., min_length=4)
    description: Optional[str] = None
    message: Optional[str] = None
    priority: Optional[str] = Field(default="medium", description="low, medium, high, critical")

    def model_post_init(self, __context):
        if not self.description and self.message:
            self.description = self.message
        elif not self.message and self.description:
            self.message = self.description


class TicketUpdateRequest(BaseModel):
    status: str = Field(default="resolved")
    admin_notes: Optional[str] = None
    resolution_notes: Optional[str] = None


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_number: str
    user_id: Optional[int] = None
    customer_name: str
    customer_email: str
    subject: str
    message: str
    priority: TicketPriority
    status: TicketStatus
    created_at: datetime


class VendorApplyRequest(BaseModel):
    user_id: Optional[int] = 1
    brand_name: Optional[str] = None
    store_name: Optional[str] = None
    business_reg_no: Optional[str] = None
    business_registration: Optional[str] = None
    category: str = "Men's Apparel"
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None

    def model_post_init(self, __context):
        if not self.brand_name and self.store_name:
            self.brand_name = self.store_name
        elif not self.store_name and self.brand_name:
            self.store_name = self.brand_name
        if not self.brand_name:
            self.brand_name = "Snitch Partner Studio"
        if not self.business_reg_no and self.business_registration:
            self.business_reg_no = self.business_registration
        elif not self.business_registration and self.business_reg_no:
            self.business_registration = self.business_reg_no
        if not self.business_reg_no:
            self.business_reg_no = "REG-SNITCH-8812"


class VendorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    store_name: str
    contact_name: str
    contact_email: str
    category: str
    status: str
    created_at: datetime


class AdminMetricsResponse(BaseModel):
    total_gmv: float
    total_sales_revenue: float
    total_orders: int
    total_users: int
    total_products: int
    open_tickets_count: int
    return_rate_percentage: float
    recent_activity: List[Dict[str, Any]] = []
