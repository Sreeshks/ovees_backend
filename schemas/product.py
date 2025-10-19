from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .category import CategoryResponse


class ProductBase(BaseModel):
    name: str
    details: Optional[str] = None
    price: float = Field(..., gt=0)
    category_id: int
    images: Optional[List[str]] = []
    stock_quantity: int = Field(default=0, ge=0)
    is_active: bool = True


class ProductCreate(ProductBase):
    product_code: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    details: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
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
