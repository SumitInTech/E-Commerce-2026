"""
Order API Router.
Registers HTTP endpoints for cart operations, checkout, status progression, and tracking.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database.supabase_client import get_db
from backend.order.schemas.order_schema import (
    CartItemAddRequest,
    CartResponse,
    CheckoutRequest,
    OrderResponse,
    OrderTrackingResponse,
    CartItemResponse
)
from backend.order.models.order_model import OrderStatus
from backend.order.controllers.order_controller import order_controller
from backend.order.services.order_service import order_service
from backend.catalog.models.catalog_model import Product

router = APIRouter(prefix="/orders", tags=["Order & Cart Service"])


@router.post("/cart/add", response_model=CartResponse)
def add_to_cart_by_session(
    req: CartItemAddRequest,
    session_id: Optional[str] = Query("cart_default_session"),
    db: Session = Depends(get_db)
):
    """Adds a garment variant to cart using session_id."""
    cart = order_service.add_to_cart(db, session_id=session_id, item_in=req)
    items_dto = []
    subtotal = 0.0
    for item in cart.items:
        prod = db.query(Product).filter(Product.id == item.product_id).first()
        p_name = prod.name if prod else "Apparel"
        p_price = prod.price if prod else 1499.0
        tot = p_price * item.quantity
        subtotal += tot
        items_dto.append(CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=p_name,
            size_label=item.size_label,
            quantity=item.quantity,
            unit_price=p_price,
            total_price=tot
        ))
    return CartResponse(
        id=cart.id,
        session_id=cart.session_id,
        items=items_dto,
        subtotal=subtotal,
        total_amount=subtotal,
        total=subtotal
    )


@router.get("/cart/{user_ref}", response_model=CartResponse)
def get_cart(user_ref: str, db: Session = Depends(get_db)):
    """Retrieves active shopping cart for a user ID or session ID."""
    if user_ref.isdigit():
        return order_controller.get_cart(db, int(user_ref))
    cart = order_service.get_or_create_cart(db, session_id=user_ref)
    items_dto = []
    subtotal = 0.0
    for item in cart.items:
        prod = db.query(Product).filter(Product.id == item.product_id).first()
        p_name = prod.name if prod else "Apparel"
        p_price = prod.price if prod else 1499.0
        tot = p_price * item.quantity
        subtotal += tot
        items_dto.append(CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=p_name,
            size_label=item.size_label,
            quantity=item.quantity,
            unit_price=p_price,
            total_price=tot
        ))
    return CartResponse(
        id=cart.id,
        session_id=cart.session_id,
        items=items_dto,
        subtotal=subtotal,
        total_amount=subtotal,
        total=subtotal
    )


@router.delete("/cart/remove/{item_id}", response_model=CartResponse)
def remove_from_cart_by_session(
    item_id: int,
    session_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Removes a line item by session ID."""
    cart = order_service.remove_from_cart(db, session_id=session_id, item_id=item_id)
    items_dto = []
    subtotal = 0.0
    for item in cart.items:
        prod = db.query(Product).filter(Product.id == item.product_id).first()
        p_name = prod.name if prod else "Apparel"
        p_price = prod.price if prod else 1499.0
        tot = p_price * item.quantity
        subtotal += tot
        items_dto.append(CartItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_name=p_name,
            size_label=item.size_label,
            quantity=item.quantity,
            unit_price=p_price,
            total_price=tot
        ))
    return CartResponse(
        id=cart.id,
        session_id=cart.session_id,
        items=items_dto,
        subtotal=subtotal,
        total_amount=subtotal,
        total=subtotal
    )


@router.post("/cart/{user_id}/items", response_model=CartResponse)
def add_to_cart(user_id: int, req: CartItemAddRequest, db: Session = Depends(get_db)):
    """Adds a garment variant to the shopping cart."""
    return order_controller.add_to_cart(db, user_id, req)


@router.delete("/cart/{user_id}/items/{item_id}", response_model=CartResponse)
def remove_from_cart(user_id: int, item_id: int, db: Session = Depends(get_db)):
    """Removes a line item from the active cart."""
    return order_controller.remove_from_cart(db, user_id, item_id)


@router.post("/checkout", response_model=OrderResponse)
def checkout(req: CheckoutRequest, db: Session = Depends(get_db)):
    """Converts active cart items into a confirmed Order with tracking ID."""
    return order_controller.checkout(db, req)


@router.get("/user/{user_id}", response_model=List[OrderResponse])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    """Retrieves order history for a buyer."""
    return order_controller.get_user_orders(db, user_id)


@router.get("/track/{order_ref}", response_model=OrderTrackingResponse)
def track_order_by_ref(order_ref: str, db: Session = Depends(get_db)):
    """Returns logistics delivery timeline by order number or order ID."""
    data = order_service.track_order(db, order_ref)
    return OrderTrackingResponse(**data)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_details(order_id: int, db: Session = Depends(get_db)):
    """Retrieves full order details including line items."""
    return order_controller.get_order_details(db, order_id)


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, new_status: OrderStatus, db: Session = Depends(get_db)):
    """Updates order fulfillment state (e.g. PACKED -> SHIPPED -> DELIVERED)."""
    return order_controller.update_status(db, order_id, new_status)


@router.get("/{order_id}/track", response_model=OrderTrackingResponse)
def track_order(order_id: int, db: Session = Depends(get_db)):
    """Returns real-time 5-stage logistics delivery timeline."""
    return order_controller.track_order(db, order_id)
