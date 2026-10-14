"""
Order & Cart Router.
Manages persistent cart additions, secure checkout, order history, and live tracking.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.schemas.order import (
    CartItemAddRequest, CartResponse, CheckoutRequest, OrderResponse, OrderStatusUpdateRequest
)
from backend.services.order_service import OrderService
from backend.services.auth_service import get_current_user, require_role

router = APIRouter(prefix="/orders", tags=["4. Order & Catalog Service"])


@router.get("/cart/{session_id}", response_model=CartResponse)
def get_cart(session_id: str, db: Session = Depends(get_db)):
    """Retrieves items in the current shopping cart."""
    return OrderService.get_cart_details(db, session_id)


@router.post("/cart/add", response_model=CartResponse)
def add_to_cart(
    req: CartItemAddRequest,
    session_id: str = Query(..., description="Unique cart session token"),
    db: Session = Depends(get_db)
):
    """Adds a sized product variant to the cart and checks real-time inventory."""
    return OrderService.add_to_cart(
        db, session_id=session_id, product_id=req.product_id, size_label=req.size_label, quantity=req.quantity
    )


@router.delete("/cart/remove/{item_id}", response_model=CartResponse)
def remove_from_cart(
    item_id: int,
    session_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """Removes a specific line item from the shopping cart."""
    return OrderService.remove_from_cart(db, session_id=session_id, item_id=item_id)


@router.post("/checkout", response_model=OrderResponse)
def checkout(
    req: CheckoutRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Converts cart into confirmed order, deducts stock, and initiates tracking."""
    user_id = current_user.id if current_user else None
    return OrderService.checkout(db, req, user_id=user_id)


@router.get("/track/{order_number}", response_model=OrderResponse)
def track_order(order_number: str, db: Session = Depends(get_db)):
    """Public tracking endpoint: returns live order lifecycle status and tracking code."""
    order = OrderService.get_order_by_number(db, order_number)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{order_number}' not found")
    return order


@router.get("", response_model=List[OrderResponse])
def list_orders(
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns recent orders (filtered for authenticated user if logged in)."""
    user_id = current_user.id if current_user else None
    return OrderService.list_orders(db, user_id=user_id)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_status(
    order_id: int,
    req: OrderStatusUpdateRequest,
    current_user: User = Depends(require_role(["seller", "admin"])),
    db: Session = Depends(get_db)
):
    """Allows sellers and operators to transition orders through fulfillment stages."""
    return OrderService.update_order_status(db, order_id, req.status, req.tracking_number)
