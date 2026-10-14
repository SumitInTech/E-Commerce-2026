"""
Catalog & Product Schemas.
"""
from typing import List, Optional
from pydantic import BaseModel


class ProductSizeResponse(BaseModel):
    id: int
    size_label: str
    stock_quantity: int
    chest_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    length_cm: Optional[float] = None

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    id: int
    category_id: int
    name: str
    slug: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    fabric: str
    garment_type: str
    fabric_stretch: str
    image_url: Optional[str] = None
    is_bestseller: bool
    is_featured: bool
    sizes: List[ProductSizeResponse] = []

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class ProductCreateRequest(BaseModel):
    category_id: int
    name: str
    slug: str
    description: str
    price: float
    original_price: Optional[float] = None
    fabric: str = "Cotton Blend"
    garment_type: str = "shirt"
    fabric_stretch: str = "none"
    image_url: Optional[str] = None
    is_bestseller: bool = False
    is_featured: bool = True
