from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
import json

from database import get_db
from models import Product, Category, Combo, ComboProduct, NewArrival, Admin, Banner
from schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ComboCreate, ComboUpdate, ComboResponse,
    NewArrivalCreate, NewArrivalResponse,
    AdminLogin, Token, AdminCreate,
    BannerCreate, BannerUpdate, BannerResponse
)
from utils.auth import (
    verify_password, get_password_hash, create_access_token, 
    get_current_admin, ACCESS_TOKEN_EXPIRE_MINUTES
)
from utils.cloudinary_config import upload_image, upload_multiple_images, delete_image

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
async def create_product(
    product_code: str = Form(...),
    name: str = Form(...),
    details: Optional[str] = Form(None),
    normal_price: float = Form(...),
    offer_price: Optional[float] = Form(None),
    category_id: int = Form(...),
    stock_quantity: int = Form(0),
    is_active: bool = Form(True),
    images: Optional[List[UploadFile]] = File(None),
    image_urls: Optional[str] = Form(None),  # JSON string of URLs if not uploading files
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Create a new product with optional image upload.
    Can accept either uploaded files or image URLs as JSON string.
    """
    # Check if product code already exists
    existing = db.query(Product).filter(Product.product_code == product_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product code already exists")
    
    # Check if category exists
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Handle images
    final_image_urls = []
    
    # If files are uploaded, upload to Cloudinary
    if images:
        for image in images:
            if not image.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail=f"File {image.filename} must be an image")
            
            result = await upload_image(image, folder=f"ovees_jewelry/products/{product_code}")
            final_image_urls.append(result["secure_url"])
    
    # If image URLs are provided as JSON string
    elif image_urls:
        try:
            final_image_urls = json.loads(image_urls)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid image_urls JSON format")
    
    # Create product
    new_product = Product(
        product_code=product_code,
        name=name,
        details=details,
        normal_price=normal_price,
        offer_price=offer_price,
        category_id=category_id,
        images=final_image_urls,
        stock_quantity=stock_quantity,
        is_active=is_active
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.put("/products/{product_code}", response_model=ProductResponse)
async def update_product(
    product_code: str,
    name: Optional[str] = Form(None),
    details: Optional[str] = Form(None),
    normal_price: Optional[float] = Form(None),
    offer_price: Optional[float] = Form(None),
    category_id: Optional[int] = Form(None),
    stock_quantity: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    image_urls: Optional[str] = Form(None),  # JSON string of URLs
    replace_images: bool = Form(False),  # If True, replace all images; if False, append
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Update a product with optional image upload.
    Can update product details and handle image uploads or URLs.
    """
    db_product = db.query(Product).filter(Product.product_code == product_code).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update basic fields
    if name is not None:
        db_product.name = name
    if details is not None:
        db_product.details = details
    if normal_price is not None:
        db_product.normal_price = normal_price
    if offer_price is not None:
        db_product.offer_price = offer_price
    if stock_quantity is not None:
        db_product.stock_quantity = stock_quantity
    if is_active is not None:
        db_product.is_active = is_active
    
    # Check if category exists if being updated
    if category_id is not None:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        db_product.category_id = category_id
    
    # Handle images
    new_image_urls = []
    
    # If files are uploaded, upload to Cloudinary
    if images:
        for image in images:
            if not image.content_type.startswith('image/'):
                raise HTTPException(status_code=400, detail=f"File {image.filename} must be an image")
            
            result = await upload_image(image, folder=f"ovees_jewelry/products/{product_code}")
            new_image_urls.append(result["secure_url"])
    
    # If image URLs are provided as JSON string
    elif image_urls:
        try:
            new_image_urls = json.loads(image_urls)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid image_urls JSON format")
    
    # Update images based on replace_images flag
    if new_image_urls:
        if replace_images:
            db_product.images = new_image_urls
        else:
            existing_images = db_product.images or []
            db_product.images = existing_images + new_image_urls
    
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


# ==================== BANNERS ====================

@router.post("/banners/upload", response_model=BannerResponse, status_code=status.HTTP_201_CREATED)
async def upload_banner(
    image: UploadFile = File(...),
    title: Optional[str] = Form(None),
    link_url: Optional[str] = Form(None),
    display_order: int = Form(0),
    is_active: bool = Form(True),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Upload a new banner image"""
    # Validate file type
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Upload to Cloudinary
    result = await upload_image(image, folder="ovees_jewelry/banners")
    
    # Create banner record
    new_banner = Banner(
        title=title,
        image_url=result["secure_url"],
        public_id=result["public_id"],
        link_url=link_url,
        display_order=display_order,
        is_active=is_active
    )
    
    db.add(new_banner)
    db.commit()
    db.refresh(new_banner)
    return new_banner


@router.post("/banners/upload-multiple", response_model=List[BannerResponse], status_code=status.HTTP_201_CREATED)
async def upload_multiple_banners(
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Upload multiple banner images at once"""
    # Validate file types
    for image in images:
        if not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail=f"File {image.filename} must be an image")
    
    # Get the highest current display_order
    max_order = db.query(Banner).count()
    
    uploaded_banners = []
    for idx, image in enumerate(images):
        # Upload to Cloudinary
        result = await upload_image(image, folder="ovees_jewelry/banners")
        
        # Create banner record
        new_banner = Banner(
            title=f"Banner {max_order + idx + 1}",
            image_url=result["secure_url"],
            public_id=result["public_id"],
            display_order=max_order + idx,
            is_active=True
        )
        
        db.add(new_banner)
        uploaded_banners.append(new_banner)
    
    db.commit()
    
    # Refresh all banners
    for banner in uploaded_banners:
        db.refresh(banner)
    
    return uploaded_banners


@router.get("/banners", response_model=List[BannerResponse])
def get_all_banners_admin(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get all banners (admin view - includes inactive)"""
    banners = db.query(Banner).order_by(Banner.display_order).offset(skip).limit(limit).all()
    return banners


@router.get("/banners/{banner_id}", response_model=BannerResponse)
def get_banner_admin(
    banner_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Get a single banner"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    return banner


@router.put("/banners/{banner_id}", response_model=BannerResponse)
def update_banner(
    banner_id: int,
    banner_update: BannerUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Update banner details"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    
    # Update fields
    update_data = banner_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(banner, key, value)
    
    db.commit()
    db.refresh(banner)
    return banner


@router.put("/banners/{banner_id}/reorder", response_model=BannerResponse)
def reorder_banner(
    banner_id: int,
    new_order: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Change the display order of a banner"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    
    old_order = banner.display_order
    
    # Update other banners' order
    if new_order < old_order:
        # Moving up: increment orders between new and old
        db.query(Banner).filter(
            Banner.display_order >= new_order,
            Banner.display_order < old_order,
            Banner.id != banner_id
        ).update({Banner.display_order: Banner.display_order + 1})
    elif new_order > old_order:
        # Moving down: decrement orders between old and new
        db.query(Banner).filter(
            Banner.display_order > old_order,
            Banner.display_order <= new_order,
            Banner.id != banner_id
        ).update({Banner.display_order: Banner.display_order - 1})
    
    # Update the banner's order
    banner.display_order = new_order
    
    db.commit()
    db.refresh(banner)
    return banner


@router.delete("/banners/{banner_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_banner(
    banner_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Delete a banner (also removes from Cloudinary)"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    
    # Delete from Cloudinary
    try:
        delete_image(banner.public_id)
    except Exception as e:
        print(f"Warning: Failed to delete image from Cloudinary: {str(e)}")
    
    # Delete from database
    db.delete(banner)
    db.commit()
    return None


@router.patch("/banners/{banner_id}/toggle", response_model=BannerResponse)
def toggle_banner(
    banner_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """Toggle active status of a banner"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=404, detail="Banner not found")
    
    banner.is_active = not banner.is_active
    db.commit()
    db.refresh(banner)
    return banner
