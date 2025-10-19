from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List, Optional

from database import get_db
from models import Product, Category, Combo, NewArrival
from schemas import ProductResponse, CategoryResponse, ComboResponse, NewArrivalResponse

router = APIRouter(tags=["Public"])


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

@router.get("/products", response_model=List[ProductResponse])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
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
    
    - **sort_by**: price_low, price_high, newest, oldest
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    - **category_id**: Filter by category
    - **search**: Search in product name and details
    - **skip**: Pagination offset
    - **limit**: Number of items per page
    """
    query = db.query(Product).filter(Product.is_active == is_active)
    
    # Apply filters
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.name.ilike(search_term)) | (Product.details.ilike(search_term))
        )
    
    # Apply sorting
    if sort_by == "price_low":
        query = query.order_by(asc(Product.price))
    elif sort_by == "price_high":
        query = query.order_by(desc(Product.price))
    elif sort_by == "newest":
        query = query.order_by(desc(Product.created_at))
    elif sort_by == "oldest":
        query = query.order_by(asc(Product.created_at))
    else:
        query = query.order_by(desc(Product.created_at))  # Default to newest
    
    # Apply pagination
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/products/{product_code}", response_model=ProductResponse)
def get_product(product_code: str, db: Session = Depends(get_db)):
    """Get a single product by product code"""
    product = db.query(Product).filter(Product.product_code == product_code).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products/category/{category_name}", response_model=List[ProductResponse])
def get_products_by_category_name(
    category_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    sort_by: Optional[str] = Query(None, regex="^(price_low|price_high|newest|oldest)$"),
    db: Session = Depends(get_db)
):
    """Get products by category name"""
    category = db.query(Category).filter(Category.name.ilike(category_name)).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    query = db.query(Product).filter(
        Product.category_id == category.id,
        Product.is_active == True
    )
    
    # Apply sorting
    if sort_by == "price_low":
        query = query.order_by(asc(Product.price))
    elif sort_by == "price_high":
        query = query.order_by(desc(Product.price))
    elif sort_by == "newest":
        query = query.order_by(desc(Product.created_at))
    elif sort_by == "oldest":
        query = query.order_by(asc(Product.created_at))
    
    products = query.offset(skip).limit(limit).all()
    return products


# ==================== SPECIAL COLLECTIONS ====================

@router.get("/products/collection/99-store", response_model=List[ProductResponse])
def get_99_store_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all products priced at ₹99"""
    products = db.query(Product).filter(
        Product.price == 99,
        Product.is_active == True
    ).offset(skip).limit(limit).all()
    return products


@router.get("/products/collection/199-store", response_model=List[ProductResponse])
def get_199_store_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all products priced at ₹199"""
    products = db.query(Product).filter(
        Product.price == 199,
        Product.is_active == True
    ).offset(skip).limit(limit).all()
    return products


# ==================== COMBOS ====================

@router.get("/combos", response_model=List[ComboResponse])
def get_combos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """Get all combos"""
    combos = db.query(Combo).filter(
        Combo.is_active == is_active
    ).offset(skip).limit(limit).all()
    return combos


@router.get("/combos/{combo_code}", response_model=ComboResponse)
def get_combo(combo_code: str, db: Session = Depends(get_db)):
    """Get a single combo by combo code"""
    combo = db.query(Combo).filter(Combo.combo_code == combo_code).first()
    if not combo:
        raise HTTPException(status_code=404, detail="Combo not found")
    return combo


# ==================== NEW ARRIVALS ====================

@router.get("/new-arrivals", response_model=List[NewArrivalResponse])
def get_new_arrivals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """Get all new arrival products"""
    new_arrivals = db.query(NewArrival).filter(
        NewArrival.is_active == is_active
    ).order_by(desc(NewArrival.added_at)).offset(skip).limit(limit).all()
    return new_arrivals


# ==================== STATISTICS ====================

@router.get("/stats/products-count")
def get_products_count(db: Session = Depends(get_db)):
    """Get product statistics"""
    total_products = db.query(Product).filter(Product.is_active == True).count()
    store_99_count = db.query(Product).filter(Product.price == 99, Product.is_active == True).count()
    store_199_count = db.query(Product).filter(Product.price == 199, Product.is_active == True).count()
    combos_count = db.query(Combo).filter(Combo.is_active == True).count()
    new_arrivals_count = db.query(NewArrival).filter(NewArrival.is_active == True).count()
    
    return {
        "total_products": total_products,
        "99_store": store_99_count,
        "199_store": store_199_count,
        "combos": combos_count,
        "new_arrivals": new_arrivals_count
    }
