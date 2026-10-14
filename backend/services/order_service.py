"""
Order Lifecycle & Cart Service.
Manages persistent shopping carts, stock reservations, order state transitions,
and end-to-end fulfillment tracking.
"""
import uuid
import random
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from backend.models import Order, OrderItem, OrderStatus, Cart, CartItem, Product, ProductSize, User
from backend.schemas.order import CheckoutRequest, CartResponse, CartItemResponse


class OrderService:
    @staticmethod
    def get_or_create_cart(db: Session, session_id: str, user_id: Optional[int] = None) -> Cart:
        cart = db.query(Cart).filter(Cart.session_id == session_id).first()
        if not cart:
            cart = Cart(session_id=session_id, user_id=user_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
        elif user_id and not cart.user_id:
            cart.user_id = user_id
            db.commit()
        return cart

    @classmethod
    def add_to_cart(cls, db: Session, session_id: str, product_id: int, size_label: str, quantity: int = 1) -> CartResponse:
        cart = cls.get_or_create_cart(db, session_id)
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Check stock
        size_record = db.query(ProductSize).filter(
            ProductSize.product_id == product_id,
            ProductSize.size_label == size_label
        ).first()
        if not size_record or size_record.stock_quantity < quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient inventory for size {size_label}")

        item = db.query(CartItem).filter(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
            CartItem.size_label == size_label
        ).first()

        if item:
            item.quantity += quantity
        else:
            item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                size_label=size_label,
                quantity=quantity
            )
            db.add(item)

        db.commit()
        return cls.get_cart_details(db, session_id)

    @classmethod
    def remove_from_cart(cls, db: Session, session_id: str, item_id: int) -> CartResponse:
        cart = cls.get_or_create_cart(db, session_id)
        item = db.query(CartItem).filter(CartItem.id == item_id, CartItem.cart_id == cart.id).first()
        if item:
            db.delete(item)
            db.commit()
        return cls.get_cart_details(db, session_id)

    @classmethod
    def get_cart_details(cls, db: Session, session_id: str) -> CartResponse:
        cart = cls.get_or_create_cart(db, session_id)
        items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()

        item_responses: List[CartItemResponse] = []
        subtotal = 0.0

        for it in items:
            p = db.query(Product).filter(Product.id == it.product_id).first()
            if p:
                tot = p.price * it.quantity
                subtotal += tot
                item_responses.append(
                    CartItemResponse(
                        id=it.id,
                        product_id=p.id,
                        product_name=p.name,
                        product_price=p.price,
                        product_image=p.image_url,
                        size_label=it.size_label,
                        quantity=it.quantity,
                        total_price=tot
                    )
                )

        tax = round(subtotal * 0.05, 2)
        shipping = 0.0 if (subtotal >= 1500.0 or subtotal == 0.0) else 99.0
        total = round(subtotal + tax + shipping, 2)

        return CartResponse(
            session_id=session_id,
            items=item_responses,
            subtotal=round(subtotal, 2),
            tax=tax,
            shipping=shipping,
            total=total
        )

    @classmethod
    def checkout(cls, db: Session, req: CheckoutRequest, user_id: Optional[int] = None) -> Order:
        if not req.cart_items:
            raise HTTPException(status_code=400, detail="Cannot checkout an empty cart")

        subtotal = 0.0
        order_items_to_create = []

        # Validate inventory and calculate totals
        for item_req in req.cart_items:
            product = db.query(Product).filter(Product.id == item_req.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product ID {item_req.product_id} not found")

            size_record = db.query(ProductSize).filter(
                ProductSize.product_id == item_req.product_id,
                ProductSize.size_label == item_req.size_label
            ).first()

            if not size_record or size_record.stock_quantity < item_req.quantity:
                raise HTTPException(status_code=400, detail=f"Stock unavailable for {product.name} (Size {item_req.size_label})")

            # Deduct stock
            size_record.stock_quantity -= item_req.quantity

            line_total = product.price * item_req.quantity
            subtotal += line_total

            order_items_to_create.append(
                OrderItem(
                    product_id=product.id,
                    product_name=product.name,
                    size_label=item_req.size_label,
                    quantity=item_req.quantity,
                    unit_price=product.price,
                    total_price=line_total
                )
            )

        tax = round(subtotal * 0.05, 2)
        shipping = 0.0 if subtotal >= 1500.0 else 99.0
        total = round(subtotal + tax + shipping, 2)

        random_suffix = random.randint(10000, 99999)
        tracking_suffix = random.randint(100000, 999999)

        order = Order(
            order_number=f"ORD-SNITCH-{random_suffix}",
            user_id=user_id,
            customer_name=req.customer_name,
            customer_email=req.customer_email,
            status=OrderStatus.CONFIRMED,
            total_amount=total,
            shipping_fee=shipping,
            tax_amount=tax,
            shipping_address=req.shipping_address,
            payment_method=req.payment_method,
            tracking_number=f"TRK-DELHIVERY-{tracking_suffix}"
        )
        db.add(order)
        db.flush()

        for oi in order_items_to_create:
            oi.order_id = order.id
            db.add(oi)

        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def get_order_by_number(db: Session, order_number: str) -> Optional[Order]:
        return db.query(Order).filter(Order.order_number == order_number).first()

    @staticmethod
    def list_orders(db: Session, user_id: Optional[int] = None, limit: int = 50) -> List[Order]:
        q = db.query(Order)
        if user_id:
            q = q.filter(Order.user_id == user_id)
        return q.order_by(Order.id.desc()).limit(limit).all()

    @staticmethod
    def update_order_status(db: Session, order_id: int, new_status: str, tracking_number: Optional[str] = None) -> Order:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        try:
            order.status = OrderStatus(new_status.lower())
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")

        if tracking_number:
            order.tracking_number = tracking_number

        db.commit()
        db.refresh(order)
        return order
