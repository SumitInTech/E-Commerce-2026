"""
Pydantic v2 Schemas for Catalog & Garment Size Specs.
"""
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ProductSizeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    size_label: str
    stock_quantity: int
    chest_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hip_cm: Optional[float] = None
    length_cm: Optional[float] = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    name: str
    slug: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    fabric: str = "Cotton Blend"
    garment_type: str = "shirt"
    fabric_stretch: str = "none"
    image_url: Optional[str] = None
    is_bestseller: bool = False
    is_featured: bool = True
    sizes: List[ProductSizeResponse] = []


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class ProductCreateRequest(BaseModel):
    category_id: int
    name: str
    slug: str
    description: Optional[str] = None
    price: float
    original_price: Optional[float] = None
    fabric: Optional[str] = "Cotton Blend"
    garment_type: Optional[str] = "shirt"
    fabric_stretch: Optional[str] = "none"
    image_url: Optional[str] = None
    is_featured: bool = True
