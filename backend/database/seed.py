"""
Seed Database with Initial Users, Streetwear Categories, Products, and Sizing Charts.
"""
from sqlalchemy.orm import Session
from backend.auth.models.user_model import User, UserRole
from backend.auth.services.auth_service import AuthService
from backend.catalog.models.catalog_model import Category, Product, ProductSize


def seed_database(db: Session) -> None:
    # 1. Seed Users if not present
    if db.query(User).count() == 0:
        admin = User(
            email="admin@snitch.com",
            hashed_password=AuthService.hash_password("Admin@12345"),
            full_name="Alexander Vance (Lead Architect)",
            role=UserRole.ADMIN,
            phone="+91 98765 00001",
            address="HQ Snitch Design Studio, Bangalore, India"
        )
        seller = User(
            email="seller@snitch.com",
            hashed_password=AuthService.hash_password("Seller@12345"),
            full_name="Urban Stitchers Mill",
            role=UserRole.SELLER,
            phone="+91 98765 00002",
            address="Textile Hub, Surat, Gujarat"
        )
        buyer = User(
            email="buyer@snitch.com",
            hashed_password=AuthService.hash_password("Buyer@12345"),
            full_name="Aryan Sharma",
            role=UserRole.BUYER,
            phone="+91 98765 00003",
            address="42 Indiranagar 100ft Rd, Bangalore"
        )
        db.add_all([admin, seller, buyer])
        db.commit()

    # 2. Seed Categories if not present
    if db.query(Category).count() == 0:
        cat_shirts = Category(
            name="Cuban Collar & Casual Shirts",
            slug="shirts",
            description="Bespoke linen, modal, and structured cotton shirts crafted for relaxed modern fits."
        )
        cat_tees = Category(
            name="Heavyweight Oversized Tees",
            slug="tees",
            description="240 GSM combed cotton drop-shoulder streetwear tees."
        )
        cat_trousers = Category(
            name="Pleated Trousers & Cargo Pants",
            slug="trousers",
            description="Tailored aesthetic bottoms featuring adjustable kinematic waistbands."
        )
        cat_jackets = Category(
            name="Structured Blazers & Jackets",
            slug="jackets",
            description="Architectural outerwear designed for effortless high-fashion layering."
        )
        db.add_all([cat_shirts, cat_tees, cat_trousers, cat_jackets])
        db.commit()

    # 3. Seed Products with multi-point anatomical size charts
    if db.query(Product).count() == 0:
        shirts_cat = db.query(Category).filter(Category.slug == "shirts").first()
        tees_cat = db.query(Category).filter(Category.slug == "tees").first()
        trousers_cat = db.query(Category).filter(Category.slug == "trousers").first()
        jackets_cat = db.query(Category).filter(Category.slug == "jackets").first()

        p1 = Product(
            name="Luxe Havana Relaxed Cuban Shirt",
            slug="luxe-havana-relaxed-cuban-shirt",
            description="Pure French flax linen shirt in matte obsidian with mother-of-pearl buttons.",
            price=2499.0,
            original_price=3499.0,
            fabric="100% French Linen",
            garment_type="shirt",
            fabric_stretch="none",
            category_id=shirts_cat.id if shirts_cat else 1,
            image_url="https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&q=80&w=800",
            is_featured=True,
            is_bestseller=True
        )
        p2 = Product(
            name="Kuro Drop-Shoulder Heavyweight Tee",
            slug="kuro-drop-shoulder-heavyweight-tee",
            description="260 GSM custom-milled combed cotton in vintage washed charcoal.",
            price=1499.0,
            original_price=1999.0,
            fabric="100% Combed Cotton",
            garment_type="t_shirt",
            fabric_stretch="low",
            category_id=tees_cat.id if tees_cat else 2,
            image_url="https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&q=80&w=800",
            is_featured=True,
            is_bestseller=False
        )
        p3 = Product(
            name="Aesthetic Double-Pleated Tailored Trousers",
            slug="aesthetic-double-pleated-tailored-trousers",
            description="Modern high-waisted relaxed drape trousers with side buckle adjusters.",
            price=2999.0,
            original_price=3999.0,
            fabric="Poly-Viscose Blend",
            garment_type="pants",
            fabric_stretch="none",
            category_id=trousers_cat.id if trousers_cat else 3,
            image_url="https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&q=80&w=800",
            is_featured=True,
            is_bestseller=True
        )
        p4 = Product(
            name="Sartorial Unstructured Wool Blazer",
            slug="sartorial-unstructured-wool-blazer",
            description="Unlined Italian virgin wool blend blazer designed for natural shoulder contour.",
            price=6499.0,
            original_price=8999.0,
            fabric="Italian Virgin Wool Blend",
            garment_type="jacket",
            fabric_stretch="low",
            category_id=jackets_cat.id if jackets_cat else 4,
            image_url="https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&q=80&w=800",
            is_featured=True,
            is_bestseller=False
        )

        db.add_all([p1, p2, p3, p4])
        db.commit()

        # Seed multi-point anatomical size charts
        size_specs = [
            # Sizing for Cuban Shirt (p1)
            ProductSize(product_id=p1.id, size_label="S", chest_cm=96.0, waist_cm=82.0, hip_cm=98.0, length_cm=72.0, stock_quantity=30),
            ProductSize(product_id=p1.id, size_label="M", chest_cm=100.0, waist_cm=86.0, hip_cm=102.0, length_cm=74.0, stock_quantity=45),
            ProductSize(product_id=p1.id, size_label="L", chest_cm=105.0, waist_cm=91.0, hip_cm=107.0, length_cm=76.0, stock_quantity=40),
            ProductSize(product_id=p1.id, size_label="XL", chest_cm=110.0, waist_cm=96.0, hip_cm=112.0, length_cm=78.0, stock_quantity=35),

            # Sizing for Heavyweight Tee (p2)
            ProductSize(product_id=p2.id, size_label="S", chest_cm=102.0, waist_cm=98.0, hip_cm=102.0, length_cm=70.0, stock_quantity=50),
            ProductSize(product_id=p2.id, size_label="M", chest_cm=106.0, waist_cm=102.0, hip_cm=106.0, length_cm=72.0, stock_quantity=70),
            ProductSize(product_id=p2.id, size_label="L", chest_cm=110.0, waist_cm=106.0, hip_cm=110.0, length_cm=74.0, stock_quantity=50),
            ProductSize(product_id=p2.id, size_label="XL", chest_cm=115.0, waist_cm=111.0, hip_cm=115.0, length_cm=76.0, stock_quantity=30),

            # Sizing for Pleated Trousers (p3)
            ProductSize(product_id=p3.id, size_label="S", chest_cm=0.0, waist_cm=78.0, hip_cm=96.0, length_cm=102.0, stock_quantity=20),
            ProductSize(product_id=p3.id, size_label="M", chest_cm=0.0, waist_cm=82.0, hip_cm=100.0, length_cm=104.0, stock_quantity=35),
            ProductSize(product_id=p3.id, size_label="L", chest_cm=0.0, waist_cm=87.0, hip_cm=105.0, length_cm=105.0, stock_quantity=25),
            ProductSize(product_id=p3.id, size_label="XL", chest_cm=0.0, waist_cm=92.0, hip_cm=110.0, length_cm=106.0, stock_quantity=10),

            # Sizing for Blazer (p4)
            ProductSize(product_id=p4.id, size_label="M", chest_cm=102.0, waist_cm=88.0, hip_cm=104.0, length_cm=76.0, stock_quantity=20),
            ProductSize(product_id=p4.id, size_label="L", chest_cm=106.0, waist_cm=92.0, hip_cm=108.0, length_cm=78.0, stock_quantity=20),
            ProductSize(product_id=p4.id, size_label="XL", chest_cm=110.0, waist_cm=96.0, hip_cm=112.0, length_cm=80.0, stock_quantity=10)
        ]
        db.add_all(size_specs)
        db.commit()

    # 4. Seed sample order for live tracking demonstration if not present
    from backend.order.models.order_model import Order, OrderItem, OrderStatus
    if db.query(Order).count() == 0:
        p1 = db.query(Product).first()
        sample_order = Order(
            order_number="ORD-SNITCH-88219",
            customer_name="Aryan Sharma",
            customer_email="buyer@snitch.com",
            status=OrderStatus.SHIPPED,
            total_amount=2499.0,
            shipping_fee=0.0,
            tax_amount=299.0,
            shipping_address="42 Indiranagar 100ft Rd, Bangalore, 560038",
            payment_method="CARD",
            tracking_number="DELHIVERY-AIR-9921"
        )
        db.add(sample_order)
        db.commit()
        if p1:
            item = OrderItem(
                order_id=sample_order.id,
                product_id=p1.id,
                product_name=p1.name,
                size_label="M",
                quantity=1,
                unit_price=2499.0,
                total_price=2499.0
            )
            db.add(item)
            db.commit()
