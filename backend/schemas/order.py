"""
Order, Checkout & Cart Schemas.
"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class CartItemAddRequest(BaseModel):
    product_id: int
    size_label: str
    quantity: int = 1


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: float
    product_image: Optional[str] = None
    size_label: str
    quantity: int
    total_price: float


class CartResponse(BaseModel):
    session_id: str
    items: List[CartItemResponse] = []
    subtotal: float = 0.0
    tax: float = 0.0
    shipping: float = 0.0
    total: float = 0.0


class CheckoutRequest(BaseModel):
    customer_name: str
    customer_email: str
    shipping_address: str
    payment_method: str = "CARD"  # CARD, UPI, COD
    cart_items: Optional[List[CartItemAddRequest]] = None


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    size_label: str
    quantity: int
    unit_price: float
    total_price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_email: str
    status: str
    total_amount: float
    shipping_fee: float
    tax_amount: float
    shipping_address: str
    payment_method: str
    tracking_number: Optional[str] = None
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderStatusUpdateRequest(BaseModel):
    status: str
    tracking_number: Optional[str] = None
