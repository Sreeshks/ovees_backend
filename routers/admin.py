from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from database import get_db
from models import Product, Category, Combo, ComboProduct, NewArrival, Admin
from schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ComboCreate, ComboUpdate, ComboResponse,
    NewArrivalCreate, NewArrivalResponse,
    AdminLogin, Token, AdminCreate
)
from utils.auth import (
    verify_password, get_password_hash, create_access_token, 
    get_current_admin, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ==================== AUTHENTICATION ====================

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register_admin(admin_data: AdminCreate, db: Session = Depends(get_db)):
    """Register a new admin (for initial setup only)"""
    # Check if admin already exists
    existing_admin = db.query(Admin).filter(Admin.username == admin_data.username).first()
    if existing_admin:
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    # Create new admin
    hashed_password = get_password_hash(admin_data.password)
    new_admin = Admin(username=admin_data.username, hashed_password=hashed_password)
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    
    return {"message": "Admin registered successfully", "username": new_admin.username}


@router.post("/login", response_model=Token)
def login(credentials: AdminLogin, db: Session = Depends(get_db)):
    """Admin login endpoint"""
    admin = db.query(Admin).filter(Admin.username == credentials.username).first()
    
    if not admin or not verify_password(credentials.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# ==================== CATEGORIES ====================

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate, 
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Create a new category"""
    # Check if category already exists
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    new_category = Category(**category.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category: CategoryUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Update a category"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Update fields
    for key, value in category.dict(exclude_unset=True).items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete a category"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has products
    if db_category.products:
        raise HTTPException(status_code=400, detail="Cannot delete category with products")
    
    db.delete(db_category)
    db.commit()
    return None


# ==================== PRODUCTS ====================

@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Create a new product"""
    # Check if product code already exists
    existing = db.query(Product).filter(Product.product_code == product.product_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product code already exists")
    
    # Check if category exists
    category = db.query(Category).filter(Category.id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.put("/products/{product_code}", response_model=ProductResponse)
def update_product(
    product_code: str,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Update a product"""
    db_product = db.query(Product).filter(Product.product_code == product_code).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update fields
    update_data = product.dict(exclude_unset=True)
    
    # Check if category exists if being updated
    if "category_id" in update_data:
        category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
    
    for key, value in update_data.items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/products/{product_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_code: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete a product"""
    db_product = db.query(Product).filter(Product.product_code == product_code).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return None


# ==================== COMBOS ====================

@router.post("/combos", response_model=ComboResponse, status_code=status.HTTP_201_CREATED)
def create_combo(
    combo: ComboCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Create a new combo"""
    # Check if combo code already exists
    existing = db.query(Combo).filter(Combo.combo_code == combo.combo_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Combo code already exists")
    
    # Verify all products exist
    product_ids = [item.product_id for item in combo.products]
    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    
    if len(products) != len(product_ids):
        raise HTTPException(status_code=404, detail="One or more products not found")
    
    # Create combo
    combo_data = combo.dict(exclude={"products"})
    new_combo = Combo(**combo_data)
    db.add(new_combo)
    db.commit()
    db.refresh(new_combo)
    
    # Add products to combo
    for item in combo.products:
        combo_product = ComboProduct(
            combo_id=new_combo.id,
            product_id=item.product_id,
            quantity=item.quantity
        )
        db.add(combo_product)
    
    db.commit()
    db.refresh(new_combo)
    return new_combo


@router.put("/combos/{combo_code}", response_model=ComboResponse)
def update_combo(
    combo_code: str,
    combo: ComboUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Update a combo"""
    db_combo = db.query(Combo).filter(Combo.combo_code == combo_code).first()
    if not db_combo:
        raise HTTPException(status_code=404, detail="Combo not found")
    
    update_data = combo.dict(exclude_unset=True, exclude={"products"})
    
    # Update combo fields
    for key, value in update_data.items():
        setattr(db_combo, key, value)
    
    # Update products if provided
    if combo.products is not None:
        # Remove existing products
        db.query(ComboProduct).filter(ComboProduct.combo_id == db_combo.id).delete()
        
        # Verify all new products exist
        product_ids = [item.product_id for item in combo.products]
        products = db.query(Product).filter(Product.id.in_(product_ids)).all()
        
        if len(products) != len(product_ids):
            raise HTTPException(status_code=404, detail="One or more products not found")
        
        # Add new products
        for item in combo.products:
            combo_product = ComboProduct(
                combo_id=db_combo.id,
                product_id=item.product_id,
                quantity=item.quantity
            )
            db.add(combo_product)
    
    db.commit()
    db.refresh(db_combo)
    return db_combo


@router.delete("/combos/{combo_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_combo(
    combo_code: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete a combo"""
    db_combo = db.query(Combo).filter(Combo.combo_code == combo_code).first()
    if not db_combo:
        raise HTTPException(status_code=404, detail="Combo not found")
    
    db.delete(db_combo)
    db.commit()
    return None


# ==================== NEW ARRIVALS ====================

@router.post("/new-arrivals", response_model=NewArrivalResponse, status_code=status.HTTP_201_CREATED)
def add_new_arrival(
    new_arrival: NewArrivalCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Add a product to new arrivals"""
    # Check if product exists
    product = db.query(Product).filter(Product.id == new_arrival.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if already in new arrivals
    existing = db.query(NewArrival).filter(NewArrival.product_id == new_arrival.product_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product already in new arrivals")
    
    new_arrival_entry = NewArrival(**new_arrival.dict())
    db.add(new_arrival_entry)
    db.commit()
    db.refresh(new_arrival_entry)
    return new_arrival_entry


@router.delete("/new-arrivals/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_new_arrival(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Remove a product from new arrivals"""
    new_arrival = db.query(NewArrival).filter(NewArrival.product_id == product_id).first()
    if not new_arrival:
        raise HTTPException(status_code=404, detail="Product not in new arrivals")
    
    db.delete(new_arrival)
    db.commit()
    return None


@router.patch("/new-arrivals/{product_id}/toggle", response_model=NewArrivalResponse)
def toggle_new_arrival(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Toggle active status of a new arrival"""
    new_arrival = db.query(NewArrival).filter(NewArrival.product_id == product_id).first()
    if not new_arrival:
        raise HTTPException(status_code=404, detail="Product not in new arrivals")
    
    new_arrival.is_active = not new_arrival.is_active
    db.commit()
    db.refresh(new_arrival)
    return new_arrival
