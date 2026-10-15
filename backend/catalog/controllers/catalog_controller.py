"""
Catalog HTTP Controller.
Coordinates requests for categories, products, and sizing charts.
"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.catalog.services.catalog_service import catalog_service
from backend.catalog.schemas.catalog_schema import (
    ProductResponse,
    CategoryResponse,
    ProductSizeResponse,
    ProductCreateRequest
)


class CatalogController:
    @staticmethod
    def list_categories(db: Session) -> List[CategoryResponse]:
        categories = catalog_service.get_categories(db)
        return [CategoryResponse.model_validate(c) for c in categories]

    @staticmethod
    def list_products(
        db: Session,
        category_id: Optional[int] = None,
        featured: Optional[bool] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[ProductResponse]:
        products = catalog_service.get_products(db, category_id=category_id, featured=featured, limit=limit, skip=skip)
        return [ProductResponse.model_validate(p) for p in products]

    @staticmethod
    def get_product(db: Session, product_id: int) -> ProductResponse:
        product = catalog_service.get_product_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return ProductResponse.model_validate(product)

    @staticmethod
    def get_product_sizes(db: Session, product_id: int) -> List[ProductSizeResponse]:
        sizes = catalog_service.get_product_sizes(db, product_id)
        return [ProductSizeResponse.model_validate(s) for s in sizes]

    @staticmethod
    def create_product(db: Session, req: ProductCreateRequest) -> ProductResponse:
        product = catalog_service.create_product(db, req)
        return ProductResponse.model_validate(product)


catalog_controller = CatalogController()
