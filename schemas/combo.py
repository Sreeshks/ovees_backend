from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .product import ProductResponse


class ComboProductItem(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class ComboBase(BaseModel):
    name: str
    description: Optional[str] = None
    combo_price: float = Field(..., gt=0)
    is_active: bool = True


class ComboCreate(ComboBase):
    combo_code: str
    products: List[ComboProductItem]  # List of products with quantities


class ComboUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    combo_price: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None
    products: Optional[List[ComboProductItem]] = None


class ComboProductResponse(BaseModel):
    product: ProductResponse
    quantity: int
    
    class Config:
        from_attributes = True


class ComboResponse(ComboBase):
    id: int
    combo_code: str
    products: List[ComboProductResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
