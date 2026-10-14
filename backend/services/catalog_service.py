"""
Catalog & Product Service.
Manages category listings, product queries, search filtering, and inventory availability.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.models import Product, Category, ProductSize
from backend.schemas.catalog import ProductCreateRequest


class CatalogService:
    @staticmethod
    def list_categories(db: Session) -> List[Category]:
        return db.query(Category).all()

    @staticmethod
    def list_products(
        db: Session,
        category_slug: Optional[str] = None,
        search: Optional[str] = None,
        garment_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Product]:
        query = db.query(Product)

        if category_slug:
            cat = db.query(Category).filter(Category.slug == category_slug).first()
            if cat:
                query = query.filter(Product.category_id == cat.id)

        if garment_type:
            query = query.filter(Product.garment_type == garment_type)

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.fabric.ilike(search_term)
                )
            )

        return query.order_by(Product.id.asc()).offset(offset).limit(limit).all()

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def get_product_by_slug(db: Session, slug: str) -> Optional[Product]:
        return db.query(Product).filter(Product.slug == slug).first()

    @staticmethod
    def create_product(db: Session, req: ProductCreateRequest) -> Product:
        prod = Product(
            category_id=req.category_id,
            name=req.name,
            slug=req.slug,
            description=req.description,
            price=req.price,
            original_price=req.original_price,
            fabric=req.fabric,
            garment_type=req.garment_type,
            fabric_stretch=req.fabric_stretch,
            image_url=req.image_url,
            is_bestseller=req.is_bestseller,
            is_featured=req.is_featured
        )
        db.add(prod)
        db.commit()
        db.refresh(prod)
        return prod
