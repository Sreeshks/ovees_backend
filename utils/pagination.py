from sqlalchemy.orm import Query
from schemas.pagination import PaginationMeta
import math


def paginate_query(query: Query, page: int, page_size: int):
    """
    Paginate a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        page: Page number (starts from 1)
        page_size: Number of items per page
        
    Returns:
        tuple: (items, pagination_meta)
    """
    # Get total count
    total_items = query.count()
    
    # Calculate total pages
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    
    # Ensure page is within bounds
    page = max(1, min(page, total_pages))
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get items for current page
    items = query.offset(offset).limit(page_size).all()
    
    # Create pagination metadata
    meta = PaginationMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1
    )
    
    return items, meta
