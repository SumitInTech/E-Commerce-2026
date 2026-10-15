"""
Pydantic v2 Schemas for Cart Management & Order Lifecycle.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from backend.order.models.order_model import OrderStatus


class CartItemAddRequest(BaseModel):
    product_id: int
    size_label: str = Field(default="M", description="Garment size: S, M, L, XL")
    quantity: int = Field(default=1, gt=0)

    # Optional alias
    size_name: Optional[str] = None

    def model_post_init(self, __context):
        if self.size_name and not self.size_label:
            self.size_label = self.size_name


class CartItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: Optional[str] = "Apparel"
    size_label: str
    quantity: int
    unit_price: float = 0.0
    total_price: float = 0.0


class CartResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    items: List[CartItemResponse] = []
    total_amount: float = 0.0
    subtotal: float = 0.0
    tax: float = 0.0
    shipping: float = 0.0
    total: float = 0.0


class CheckoutRequest(BaseModel):
    user_id: Optional[int] = 1
    customer_name: Optional[str] = "Vikram Seth"
    customer_email: Optional[str] = "vikram@example.com"
    shipping_address: str
    payment_method: str = "CARD"
    cart_items: Optional[List[CartItemAddRequest]] = None


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name: str
    size_label: str
    quantity: int
    unit_price: float
    total_price: float


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    user_id: Optional[int] = None
    customer_name: str
    customer_email: str
    total_amount: float
    shipping_address: str
    status: str
    tracking_number: Optional[str] = None
    created_at: datetime
    items: List[OrderItemResponse] = []


class OrderTrackingResponse(BaseModel):
    order_id: Optional[int] = None
    order_number: Optional[str] = None
    status: str
    tracking_number: Optional[str] = None
    estimated_delivery: str
    timeline: List[dict] = []
