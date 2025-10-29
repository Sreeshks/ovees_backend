from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .category import CategoryResponse


class ProductBase(BaseModel):
    name: str
    details: Optional[str] = None
    # allow zero prices in existing data; response serialization previously failed
    # for products with 0.0 price. Use ge=0 to accept zero as valid.
    normal_price: float = Field(..., ge=0, description="Original/MRP price")
    offer_price: Optional[float] = Field(None, ge=0, description="Discounted/Offer price (optional)")
    category_id: int
    images: Optional[List[str]] = []
    stock_quantity: int = Field(default=0, ge=0)
    is_active: bool = True


class ProductCreate(ProductBase):
    product_code: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    details: Optional[str] = None
    # allow updating to zero as well
    normal_price: Optional[float] = Field(None, ge=0)
    offer_price: Optional[float] = Field(None, ge=0)
    category_id: Optional[int] = None
    images: Optional[List[str]] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    product_code: str
    category: CategoryResponse
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
