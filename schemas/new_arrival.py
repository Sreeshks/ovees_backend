from pydantic import BaseModel
from datetime import datetime
from .product import ProductResponse


class NewArrivalCreate(BaseModel):
    product_id: int


class NewArrivalResponse(BaseModel):
    id: int
    product: ProductResponse
    is_active: bool
    added_at: datetime
    
    class Config:
        from_attributes = True
