from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base


class Combo(Base):
    __tablename__ = "combos"
    
    id = Column(Integer, primary_key=True, index=True)
    combo_code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    combo_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    products = relationship("ComboProduct", back_populates="combo")


class ComboProduct(Base):
    """Junction table for Combo and Products (many-to-many)"""
    __tablename__ = "combo_products"
    
    id = Column(Integer, primary_key=True, index=True)
    combo_id = Column(Integer, ForeignKey("combos.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)  # Quantity of this product in the combo
    
    # Relationships
    combo = relationship("Combo", back_populates="products")
    product = relationship("Product", back_populates="combo_products")
