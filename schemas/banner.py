from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BannerBase(BaseModel):
    title: Optional[str] = None
    link_url: Optional[str] = None
    display_order: int = 0
    is_active: bool = True


class BannerCreate(BannerBase):
    image_url: str
    public_id: str


class BannerUpdate(BaseModel):
    title: Optional[str] = None
    link_url: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class BannerResponse(BannerBase):
    id: int
    image_url: str
    public_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
