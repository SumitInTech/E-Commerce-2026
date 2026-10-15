"""
Catalog API Router.
Registers HTTP endpoints for apparel collections, product queries, and size specifications.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.supabase_client import get_db
from backend.catalog.schemas.catalog_schema import (
    ProductResponse,
    CategoryResponse,
    ProductSizeResponse,
    ProductCreateRequest
)
from backend.catalog.controllers.catalog_controller import catalog_controller

router = APIRouter(prefix="/catalog", tags=["Catalog Service"])


@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Retrieves all luxury streetwear apparel categories."""
    return catalog_controller.list_categories(db)


@router.get("/products", response_model=List[ProductResponse])
def get_products(
    category_id: Optional[int] = None,
    featured: Optional[bool] = None,
    limit: int = 50,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    """Retrieves apparel listings with filtering by category or featured status."""
    return catalog_controller.list_products(db, category_id=category_id, featured=featured, limit=limit, skip=skip)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Retrieves product details including multi-point sizing specifications."""
    return catalog_controller.get_product(db, product_id)


@router.get("/sizes/{product_id}", response_model=List[ProductSizeResponse])
def get_product_sizes(product_id: int, db: Session = Depends(get_db)):
    """Retrieves anatomical chest, waist, and hip size charts for a garment."""
    return catalog_controller.get_product_sizes(db, product_id)


@router.post("/products", response_model=ProductResponse)
def create_product(req: ProductCreateRequest, db: Session = Depends(get_db)):
    """Adds a new apparel item to the catalog (Seller/Admin)."""
    return catalog_controller.create_product(db, req)
