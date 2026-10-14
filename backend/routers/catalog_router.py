"""
Catalog Service Router.
Exposes public product listings, category taxonomy, and size chart specifications.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import User
from backend.schemas.catalog import ProductResponse, CategoryResponse, ProductCreateRequest
from backend.services.catalog_service import CatalogService
from backend.services.auth_service import require_role

router = APIRouter(prefix="/catalog", tags=["4. Order & Catalog Service"])


@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Retrieves all fashion categories."""
    return CatalogService.list_categories(db)


@router.get("/products", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = Query(None, description="Category slug"),
    garment_type: Optional[str] = Query(None, description="shirt, t_shirt, jacket, pants"),
    search: Optional[str] = Query(None, description="Search keyword"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Lists catalog products with optional category, type, and keyword filtering."""
    return CatalogService.list_products(
        db, category_slug=category, search=search, garment_type=garment_type, limit=limit, offset=offset
    )


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Fetches single product details with complete multi-point size chart."""
    prod = CatalogService.get_product_by_id(db, product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod


@router.post("/products", response_model=ProductResponse)
def create_product(
    req: ProductCreateRequest,
    current_user: User = Depends(require_role(["seller", "admin"])),
    db: Session = Depends(get_db)
):
    """Enables sellers and admins to add new streetwear apparel to the catalog."""
    return CatalogService.create_product(db, req)
