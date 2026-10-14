"""
Database Engine, Session Management, and Database Seeding.
Configures SQLite/PostgreSQL with connection pooling, declarative schemas,
and pre-populates seed data reflecting Snitch-inspired luxury streetwear catalogs.
"""
from typing import Generator
import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.config import settings
from backend.models import (
    Base, User, UserRole,
    Category, Product, ProductSize,
    Order, OrderItem, OrderStatus,
    SupportTicket, TicketPriority, TicketStatus
)

# SQLite concurrency configuration
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    """Deterministic PBKDF2 password hashing for initial seeds."""
    salt = "snitch_luxury_streetwear_salt"
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return key.hex()


def seed_database(db: Session) -> None:
    """Populates database with initial admin, seller, buyer, and Snitch-style catalog."""
    # 1. Seed Users if not present
    if db.query(User).count() == 0:
        admin = User(
            email="admin@snitch.com",
            hashed_password=hash_password("Admin@12345"),
            full_name="Alexander Vance (Lead Architect)",
            role=UserRole.ADMIN,
            phone="+91 98765 00001",
            address="HQ Snitch Design Studio, Bangalore, India"
        )
        seller = User(
            email="seller@snitch.com",
            hashed_password=hash_password("Seller@12345"),
            full_name="Urban Stitchers Mill",
            role=UserRole.SELLER,
            phone="+91 98765 00002",
            address="Textile Hub, Surat, Gujarat"
        )
        buyer = User(
            email="buyer@snitch.com",
            hashed_password=hash_password("Buyer@12345"),
            full_name="Aryan Sharma",
            role=UserRole.BUYER,
            phone="+91 98765 00003",
            address="402 Skylark Apts, Indiranagar, Bangalore, 560038"
        )
        db.add_all([admin, seller, buyer])
        db.commit()

    # 2. Seed Categories & Products if not present
    if db.query(Category).count() == 0:
        cat_shirts = Category(
            name="Luxury Oversized Shirts",
            slug="shirts",
            description="Linen blends, cuban camp collars, and relaxed silhouettes.",
            image_url="https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&auto=format&fit=crop&q=80"
        )
        cat_tees = Category(
            name="Modern Streetwear Tees",
            slug="tees",
            description="240 GSM heavy jersey cotton with dropped shoulders.",
            image_url="https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80"
        )
        cat_pants = Category(
            name="Korean Relaxed Trousers",
            slug="trousers",
            description="Pleated front, drapey twill fabrics, and tapered ankles.",
            image_url="https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600&auto=format&fit=crop&q=80"
        )
        cat_jackets = Category(
            name="Structured Jackets & Blazers",
            slug="jackets",
            description="Vegan leather bombers, boxy blazers, and utility overshirts.",
            image_url="https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&auto=format&fit=crop&q=80"
        )
        cat_acc = Category(
            name="Accessories & Street Essentials",
            slug="accessories",
            description="Minimalist leather belts, metallic chains, and caps.",
            image_url="https://images.unsplash.com/photo-1576053139778-7e32f2ae3cfd?w=600&auto=format&fit=crop&q=80"
        )
        db.add_all([cat_shirts, cat_tees, cat_pants, cat_jackets, cat_acc])
        db.commit()

        # Seed Products with accurate Size Specs for AI Kinematic Ease
        products_data = [
            {
                "cat": cat_shirts,
                "name": "Capri Cuban Linen Camp Shirt",
                "slug": "capri-cuban-linen-camp-shirt",
                "desc": "Airy breathable pure European flax linen cut in a contemporary relaxed fit. Features notch cuban lapels, pearl buttons, and straight boxy hem.",
                "price": 1899.0,
                "orig": 2499.0,
                "fabric": "100% Pure Flax Linen",
                "type": "shirt",
                "stretch": "none",
                "bestseller": True,
                "img": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80",
                "sizes": [
                    {"label": "S", "stock": 45, "chest": 96.0, "waist": 88.0, "hip": 98.0, "len": 71.0},
                    {"label": "M", "stock": 60, "chest": 102.0, "waist": 94.0, "hip": 104.0, "len": 73.0},
                    {"label": "L", "stock": 50, "chest": 108.0, "waist": 100.0, "hip": 110.0, "len": 75.0},
                    {"label": "XL", "stock": 35, "chest": 114.0, "waist": 106.0, "hip": 116.0, "len": 77.0},
                    {"label": "XXL", "stock": 20, "chest": 122.0, "waist": 114.0, "hip": 124.0, "len": 79.0},
                ]
            },
            {
                "cat": cat_shirts,
                "name": "Onyx Midnight Corduroy Overshirt",
                "slug": "onyx-midnight-corduroy-overshirt",
                "desc": "Heavy 8-wale ribbed corduroy finished in deep charcoal onyx. Ideal for layering over t-shirts in chill weather.",
                "price": 2299.0,
                "orig": 2999.0,
                "fabric": "98% Cotton, 2% Spandex",
                "type": "shirt",
                "stretch": "low",
                "bestseller": True,
                "img": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&auto=format&fit=crop&q=80",
                "sizes": [
                    {"label": "S", "stock": 30, "chest": 98.0, "waist": 90.0, "hip": 100.0, "len": 72.0},
                    {"label": "M", "stock": 55, "chest": 104.0, "waist": 96.0, "hip": 106.0, "len": 74.0},
                    {"label": "L", "stock": 40, "chest": 110.0, "waist": 102.0, "hip": 112.0, "len": 76.0},
                    {"label": "XL", "stock": 25, "chest": 116.0, "waist": 108.0, "hip": 118.0, "len": 78.0},
                ]
            },
            {
                "cat": cat_tees,
                "name": "Acid Wash Heavyweight Oversized Tee",
                "slug": "acid-wash-heavyweight-oversized-tee",
                "desc": "Custom mineral-washed 260 GSM combed cotton. Featuring dropped shoulder seams and thick ribbed collar that never sags.",
                "price": 1299.0,
                "orig": 1799.0,
                "fabric": "100% Combed Cotton Jersey",
                "type": "t_shirt",
                "stretch": "low",
                "bestseller": True,
                "img": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=600&auto=format&fit=crop&q=80",
                "sizes": [
                    {"label": "S", "stock": 50, "chest": 104.0, "waist": 102.0, "hip": 104.0, "len": 73.0},
                    {"label": "M", "stock": 75, "chest": 110.0, "waist": 108.0, "hip": 110.0, "len": 75.0},
                    {"label": "L", "stock": 60, "chest": 116.0, "waist": 114.0, "hip": 116.0, "len": 77.0},
                    {"label": "XL", "stock": 40, "chest": 124.0, "waist": 122.0, "hip": 124.0, "len": 79.0},
                ]
            },
            {
                "cat": cat_tees,
                "name": "Raw Edge Minimalist Essential Tee",
                "slug": "raw-edge-minimalist-essential-tee",
                "desc": "Clean luxury basic tailored from Turkish supima cotton with distressed raw sleeve hems.",
                "price": 999.0,
                "orig": 1399.0,
                "fabric": "Supima Cotton Blend",
                "type": "t_shirt",
                "stretch": "medium",
                "bestseller": False,
                "img": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80",
                "sizes": [
                    {"label": "S", "stock": 40, "chest": 96.0, "waist": 92.0, "hip": 96.0, "len": 70.0},
                    {"label": "M", "stock": 50, "chest": 102.0, "waist": 98.0, "hip": 102.0, "len": 72.0},
                    {"label": "L", "stock": 45, "chest": 108.0, "waist": 104.0, "hip": 108.0, "len": 74.0},
                    {"label": "XL", "stock": 30, "chest": 114.0, "waist": 110.0, "hip": 114.0, "len": 76.0},
                ]
            },
            {
                "cat": cat_pants,
                "name": "Seoul Double-Pleated Relaxed Trousers",
                "slug": "seoul-double-pleated-relaxed-trousers",
                "desc": "High-waisted tailored pants inspired by contemporary Korean menswear. Features deep double front pleats and fluid silhouette.",
                "price": 2499.0,
                "orig": 3299.0,
                "fabric": "Poly-Viscose Stretch Twill",
                "type": "pants",
                "stretch": "low",
                "bestseller": True,
                "img": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600&auto=format&fit=crop&q=80",
                "sizes": [
                    {"label": "S", "stock": 35, "chest": 0.0, "waist": 76.0, "hip": 96.0, "len": 102.0},
                    {"label": "M", "stock": 50, "chest": 0.0, "waist": 82.0, "hip": 102.0, "len": 104.0},
                    {"label": "L", "stock": 45, "chest": 0.0, "waist": 88.0, "hip": 108.0, "len": 106.0},
                    {"label": "XL", "stock": 25, "chest": 0.0, "waist": 94.0, "hip": 114.0, "len": 108.0},
                ]
            },
            {
                "cat": cat_jackets,
                "name": "Matte Black Vegan Leather Moto Jacket",
                "slug": "matte-black-vegan-leather-moto-jacket",
                "desc": "Buttery soft animal-free vegan leather jacket with silver industrial hardware, asymmetrical zipper, and quilted satin lining.",
                "price": 4499.0,
                "orig": 5999.0,
                "fabric": "Premium PU Leather & Poly Satin",
                "type": "jacket",
                "stretch": "none",
                "bestseller": True,
                "img": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&auto=format&fit=crop&q=80",
                "sizes": [
                    {"label": "S", "stock": 20, "chest": 104.0, "waist": 96.0, "hip": 102.0, "len": 66.0},
                    {"label": "M", "stock": 35, "chest": 110.0, "waist": 102.0, "hip": 108.0, "len": 68.0},
                    {"label": "L", "stock": 30, "chest": 116.0, "waist": 108.0, "hip": 114.0, "len": 70.0},
                    {"label": "XL", "stock": 15, "chest": 124.0, "waist": 116.0, "hip": 122.0, "len": 72.0},
                ]
            }
        ]

        for p_data in products_data:
            p = Product(
                category_id=p_data["cat"].id,
                name=p_data["name"],
                slug=p_data["slug"],
                description=p_data["desc"],
                price=p_data["price"],
                original_price=p_data["orig"],
                fabric=p_data["fabric"],
                garment_type=p_data["type"],
                fabric_stretch=p_data["stretch"],
                is_bestseller=p_data["bestseller"],
                image_url=p_data["img"]
            )
            db.add(p)
            db.flush()

            for s_data in p_data["sizes"]:
                ps = ProductSize(
                    product_id=p.id,
                    size_label=s_data["label"],
                    stock_quantity=s_data["stock"],
                    chest_cm=s_data["chest"],
                    waist_cm=s_data["waist"],
                    hip_cm=s_data["hip"],
                    length_cm=s_data["len"]
                )
                db.add(ps)

        db.commit()

    # 3. Seed demo initial order & ticket if empty
    if db.query(Order).count() == 0:
        demo_order = Order(
            order_number="ORD-SNITCH-88219",
            user_id=3,
            customer_name="Aryan Sharma",
            customer_email="buyer@snitch.com",
            status=OrderStatus.CONFIRMED,
            total_amount=3198.0,
            shipping_fee=0.0,
            tax_amount=287.82,
            shipping_address="402 Skylark Apts, Indiranagar, Bangalore, 560038",
            payment_method="UPI",
            tracking_number="TRK-DELHIVERY-992104"
        )
        db.add(demo_order)
        db.flush()

        item1 = OrderItem(
            order_id=demo_order.id,
            product_id=1,
            product_name="Capri Cuban Linen Camp Shirt",
            size_label="M",
            quantity=1,
            unit_price=1899.0,
            total_price=1899.0
        )
        item2 = OrderItem(
            order_id=demo_order.id,
            product_id=3,
            product_name="Acid Wash Heavyweight Oversized Tee",
            size_label="M",
            quantity=1,
            unit_price=1299.0,
            total_price=1299.0
        )
        db.add_all([item1, item2])

        ticket = SupportTicket(
            ticket_number="TCK-9901",
            user_id=3,
            customer_name="Aryan Sharma",
            customer_email="buyer@snitch.com",
            subject="Exchange size inquiry for linen shirt",
            message="Hi, I used the AI Fit finder which recommended Size M. Just double checking if linen shrinks after cold washing?",
            priority=TicketPriority.MEDIUM,
            status=TicketStatus.OPEN,
            admin_notes="Our linen is pre-shrunk; advise cold gentle wash and hang dry."
        )
        db.add(ticket)
        db.commit()


def init_db() -> None:
    """Creates database schema and executes seed routines."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
