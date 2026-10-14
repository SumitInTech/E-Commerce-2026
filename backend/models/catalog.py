"""
Catalog & Inventory Database Models.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.models.user import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=True)

    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(255), index=True, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    fabric = Column(String(100), default="Cotton Blend")
    garment_type = Column(String(50), default="shirt")  # shirt, t_shirt, jacket, pants
    fabric_stretch = Column(String(50), default="none")  # none, low, medium, high
    image_url = Column(String(500), nullable=True)
    is_bestseller = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    sizes = relationship("ProductSize", back_populates="product", cascade="all, delete-orphan")


class ProductSize(Base):
    __tablename__ = "product_sizes"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    size_label = Column(String(10), nullable=False)  # XS, S, M, L, XL, XXL
    stock_quantity = Column(Integer, default=50)
    chest_cm = Column(Float, nullable=True)
    waist_cm = Column(Float, nullable=True)
    hip_cm = Column(Float, nullable=True)
    length_cm = Column(Float, nullable=True)

    product = relationship("Product", back_populates="sizes")
