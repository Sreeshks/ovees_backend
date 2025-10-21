from pydantic import BaseModel, Field
from typing import List, TypeVar, Generic, Optional

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination query parameters"""
    page: int = Field(default=1, ge=1, description="Page number (starts from 1)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page (max 100)")


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    meta: PaginationMeta
    
    class Config:
        from_attributes = True
