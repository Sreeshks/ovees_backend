from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    details = Column(String, nullable=True)
    price = Column(Float, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    images = Column(JSON, default=list)  # List of image URLs
    stock_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    combo_products = relationship("ComboProduct", back_populates="product")
