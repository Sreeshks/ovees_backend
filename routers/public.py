from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List, Optional

from database import get_db
from models import Product, Category, Combo, NewArrival, Banner
from schemas import ProductResponse, CategoryResponse, ComboResponse, NewArrivalResponse, BannerResponse
from schemas import PaginatedResponse
from utils.cloudinary_config import get_optimized_url, get_thumbnail_url
from utils.pagination import paginate_query

router = APIRouter(tags=["Public"])


# ==================== BANNERS ====================

@router.get("/banners", response_model=List[BannerResponse])
def get_active_banners(
    db: Session = Depends(get_db)
):
    """Get all active banners ordered by display_order"""
    banners = db.query(Banner).filter(
        Banner.is_active == True
    ).order_by(Banner.display_order).all()
    return banners


# ==================== CATEGORIES ====================

@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(Category).all()
    return categories


@router.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """Get a single category"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


# ==================== PRODUCTS ====================

@router.get("/products", response_model=PaginatedResponse[ProductResponse])
def get_products(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    sort_by: Optional[str] = Query(None, regex="^(price_low|price_high|newest|oldest)$"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """
    Get all products with filtering and sorting options
    
    - **page**: Page number (starts from 1)
    - **page_size**: Number of items per page (max 100)
    - **sort_by**: price_low, price_high, newest, oldest
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    - **category_id**: Filter by category
    - **search**: Search in product name and details
    """
    query = db.query(Product).filter(Product.is_active == is_active)
    
    # Apply filters
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if min_price is not None:
        # Check either offer_price (if exists) or normal_price
        from sqlalchemy import or_, and_, case
        query = query.filter(
            or_(
                and_(Product.offer_price.isnot(None), Product.offer_price >= min_price),
                and_(Product.offer_price.is_(None), Product.normal_price >= min_price)
            )
        )
    
    if max_price is not None:
        # Check either offer_price (if exists) or normal_price
        from sqlalchemy import or_, and_
        query = query.filter(
            or_(
                and_(Product.offer_price.isnot(None), Product.offer_price <= max_price),
                and_(Product.offer_price.is_(None), Product.normal_price <= max_price)
            )
        )
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_term)) | (Product.details.ilike(search_term))
        )
    
    # Apply sorting
    if sort_by == "price_low":
        # Sort by effective price (offer_price if available, else normal_price)
        from sqlalchemy import case
        effective_price = case(
            (Product.offer_price.isnot(None), Product.offer_price),
            else_=Product.normal_price
        )
        query = query.order_by(asc(effective_price))
    elif sort_by == "price_high":
        from sqlalchemy import case
        effective_price = case(
            (Product.offer_price.isnot(None), Product.offer_price),
            else_=Product.normal_price
        )
        query = query.order_by(desc(effective_price))
    elif sort_by == "newest":
        query = query.order_by(desc(Product.created_at))
    elif sort_by == "oldest":
        query = query.order_by(asc(Product.created_at))
    else:
        query = query.order_by(desc(Product.created_at))  # Default to newest
    
    # Apply pagination
    items, meta = paginate_query(query, page, page_size)
    return PaginatedResponse(items=items, meta=meta)


@router.get("/products/{product_code}", response_model=ProductResponse)
def get_product(product_code: str, db: Session = Depends(get_db)):
    """Get a single product by product code"""
    product = db.query(Product).filter(Product.product_code == product_code).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products/category/{category_name}", response_model=PaginatedResponse[ProductResponse])
def get_products_by_category_name(
    category_name: str,
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    sort_by: Optional[str] = Query(None, regex="^(price_low|price_high|newest|oldest)$"),
    db: Session = Depends(get_db)
):
    """Get products by category name with pagination"""
    category = db.query(Category).filter(Category.name.ilike(category_name)).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    query = db.query(Product).filter(
        Product.category_id == category.id,
        Product.is_active == True
    )
    
    # Apply sorting
    if sort_by == "price_low":
        from sqlalchemy import case
        effective_price = case(
            (Product.offer_price.isnot(None), Product.offer_price),
            else_=Product.normal_price
        )
        query = query.order_by(asc(effective_price))
    elif sort_by == "price_high":
        from sqlalchemy import case
        effective_price = case(
            (Product.offer_price.isnot(None), Product.offer_price),
            else_=Product.normal_price
        )
        query = query.order_by(desc(effective_price))
    elif sort_by == "newest":
        query = query.order_by(desc(Product.created_at))
    elif sort_by == "oldest":
        query = query.order_by(asc(Product.created_at))
    
    items, meta = paginate_query(query, page, page_size)
    return PaginatedResponse(items=items, meta=meta)


# ==================== SPECIAL COLLECTIONS ====================

@router.get("/products/collection/99-store", response_model=PaginatedResponse[ProductResponse])
def get_99_store_products(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    db: Session = Depends(get_db)
):
    """Get all products with effective price of ₹99 (either offer_price or normal_price)"""
    from sqlalchemy import or_, and_
    query = db.query(Product).filter(
        or_(
            and_(Product.offer_price.isnot(None), Product.offer_price == 99),
            and_(Product.offer_price.is_(None), Product.normal_price == 99)
        ),
        Product.is_active == True
    ).order_by(desc(Product.created_at))
    
    items, meta = paginate_query(query, page, page_size)
    return PaginatedResponse(items=items, meta=meta)


@router.get("/products/collection/199-store", response_model=PaginatedResponse[ProductResponse])
def get_199_store_products(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    db: Session = Depends(get_db)
):
    """Get all products with effective price of ₹199 (either offer_price or normal_price)"""
    from sqlalchemy import or_, and_
    query = db.query(Product).filter(
        or_(
            and_(Product.offer_price.isnot(None), Product.offer_price == 199),
            and_(Product.offer_price.is_(None), Product.normal_price == 199)
        ),
        Product.is_active == True
    ).order_by(desc(Product.created_at))
    
    items, meta = paginate_query(query, page, page_size)
    return PaginatedResponse(items=items, meta=meta)


# ==================== COMBOS ====================

@router.get("/combos", response_model=PaginatedResponse[ComboResponse])
def get_combos(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """Get all combos with pagination"""
    query = db.query(Combo).filter(
        Combo.is_active == is_active
    ).order_by(desc(Combo.created_at))
    
    items, meta = paginate_query(query, page, page_size)
    return PaginatedResponse(items=items, meta=meta)


@router.get("/combos/{combo_code}", response_model=ComboResponse)
def get_combo(combo_code: str, db: Session = Depends(get_db)):
    """Get a single combo by combo code"""
    combo = db.query(Combo).filter(Combo.combo_code == combo_code).first()
    if not combo:
        raise HTTPException(status_code=404, detail="Combo not found")
    return combo


# ==================== NEW ARRIVALS ====================

@router.get("/new-arrivals", response_model=PaginatedResponse[NewArrivalResponse])
def get_new_arrivals(
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (max 100)"),
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """Get all new arrival products with pagination"""
    query = db.query(NewArrival).filter(
        NewArrival.is_active == is_active
    ).order_by(desc(NewArrival.added_at))
    
    items, meta = paginate_query(query, page, page_size)
    return PaginatedResponse(items=items, meta=meta)


# ==================== STATISTICS ====================

@router.get("/stats/products-count")
def get_products_count(db: Session = Depends(get_db)):
    """Get product statistics"""
    from sqlalchemy import or_, and_
    total_products = db.query(Product).filter(Product.is_active == True).count()
    
    # Count products where effective price is 99
    store_99_count = db.query(Product).filter(
        or_(
            and_(Product.offer_price.isnot(None), Product.offer_price == 99),
            and_(Product.offer_price.is_(None), Product.normal_price == 99)
        ),
        Product.is_active == True
    ).count()
    
    # Count products where effective price is 199
    store_199_count = db.query(Product).filter(
        or_(
            and_(Product.offer_price.isnot(None), Product.offer_price == 199),
            and_(Product.offer_price.is_(None), Product.normal_price == 199)
        ),
        Product.is_active == True
    ).count()
    
    combos_count = db.query(Combo).filter(Combo.is_active == True).count()
    new_arrivals_count = db.query(NewArrival).filter(NewArrival.is_active == True).count()
    
    return {
        "total_products": total_products,
        "99_store": store_99_count,
        "199_store": store_199_count,
        "combos": combos_count,
        "new_arrivals": new_arrivals_count
    }


# ==================== IMAGE UTILITIES ====================

@router.get("/image/optimized")
def get_optimized_image_url(
    public_id: str = Query(..., description="Cloudinary public ID of the image"),
    width: Optional[int] = Query(None, description="Desired width"),
    height: Optional[int] = Query(None, description="Desired height")
):
    """Get an optimized URL for a Cloudinary image"""
    try:
        url = get_optimized_url(public_id, width, height)
        return {
            "public_id": public_id,
            "optimized_url": url
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate optimized URL: {str(e)}")


@router.get("/image/thumbnail")
def get_thumbnail_image_url(
    public_id: str = Query(..., description="Cloudinary public ID of the image"),
    width: int = Query(300, description="Thumbnail width"),
    height: int = Query(300, description="Thumbnail height")
):
    """Get a thumbnail URL for a Cloudinary image"""
    try:
        url = get_thumbnail_url(public_id, width, height)
        return {
            "public_id": public_id,
            "thumbnail_url": url,
            "dimensions": {"width": width, "height": height}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate thumbnail URL: {str(e)}")
