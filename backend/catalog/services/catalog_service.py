"""
Catalog Business Domain Service.
Handles apparel listings, multi-point size specifications, and inventory checks.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.catalog.models.catalog_model import Category, Product, ProductSize
from backend.catalog.schemas.catalog_schema import ProductCreateRequest


class CatalogService:
    @staticmethod
    def get_categories(db: Session) -> List[Category]:
        return db.query(Category).all()

    @staticmethod
    def get_products(
        db: Session,
        category_id: Optional[int] = None,
        featured: Optional[bool] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Product]:
        query = db.query(Product)
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if featured is not None:
            query = query.filter(Product.is_featured == featured)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def get_product_by_slug(db: Session, slug: str) -> Optional[Product]:
        return db.query(Product).filter(Product.slug == slug).first()

    @staticmethod
    def get_product_sizes(db: Session, product_id: int) -> List[ProductSize]:
        return db.query(ProductSize).filter(ProductSize.product_id == product_id).all()

    @staticmethod
    def create_product(db: Session, req: ProductCreateRequest) -> Product:
        product = Product(
            category_id=req.category_id,
            name=req.name,
            slug=req.slug,
            description=req.description,
            price=req.price,
            original_price=req.original_price,
            fabric=req.fabric or "Cotton Blend",
            garment_type=req.garment_type or "shirt",
            fabric_stretch=req.fabric_stretch or "none",
            image_url=req.image_url,
            is_featured=req.is_featured
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product


catalog_service = CatalogService()
