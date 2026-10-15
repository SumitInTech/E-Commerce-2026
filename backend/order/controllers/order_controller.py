"""
Order & Cart HTTP Controller.
Unpacks cart actions, executes checkout transactions, and coordinates order tracking.
"""
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.order.services.order_service import order_service
from backend.order.models.order_model import OrderStatus
from backend.order.schemas.order_schema import (
    CartItemAddRequest,
    CartResponse,
    CheckoutRequest,
    OrderResponse,
    OrderTrackingResponse,
    CartItemResponse
)
from backend.catalog.models.catalog_model import Product


class OrderController:
    @staticmethod
    def get_cart(db: Session, user_id: int) -> CartResponse:
        cart = order_service.get_or_create_cart(db, user_id=user_id)
        items_dto = []
        total = 0.0
        for item in cart.items:
            prod = db.query(Product).filter(Product.id == item.product_id).first()
            p_name = prod.name if prod else "Apparel"
            p_price = prod.price if prod else 1499.0
            item_total = p_price * item.quantity
            total += item_total
            items_dto.append(CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=p_name,
                size_label=item.size_label,
                quantity=item.quantity,
                unit_price=p_price,
                total_price=item_total
            ))
        return CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            session_id=cart.session_id,
            items=items_dto,
            total_amount=total,
            subtotal=total,
            total=total
        )

    @classmethod
    def add_to_cart(cls, db: Session, user_id: int, req: CartItemAddRequest) -> CartResponse:
        try:
            order_service.add_to_cart(db=db, user_id=user_id, item_in=req)
            return cls.get_cart(db, user_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @classmethod
    def remove_from_cart(cls, db: Session, user_id: int, item_id: int) -> CartResponse:
        order_service.remove_from_cart(db, user_id, item_id)
        return cls.get_cart(db, user_id)

    @staticmethod
    def checkout(db: Session, req: CheckoutRequest) -> OrderResponse:
        try:
            order = order_service.checkout(db, req)
            return OrderResponse.model_validate(order)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    def get_user_orders(db: Session, user_id: int) -> List[OrderResponse]:
        orders = order_service.get_orders_for_user(db, user_id)
        return [OrderResponse.model_validate(o) for o in orders]

    @staticmethod
    def get_order_details(db: Session, order_id: int) -> OrderResponse:
        order = order_service.get_order_by_ref(db, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return OrderResponse.model_validate(order)

    @staticmethod
    def update_status(db: Session, order_id: int, new_status: OrderStatus) -> OrderResponse:
        try:
            order = order_service.update_order_status(db, order_id, new_status)
            return OrderResponse.model_validate(order)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @staticmethod
    def track_order(db: Session, order_ref: str) -> OrderTrackingResponse:
        try:
            data = order_service.track_order(db, order_ref)
            return OrderTrackingResponse(**data)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


order_controller = OrderController()
