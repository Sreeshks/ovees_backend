from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base


class NewArrival(Base):
    __tablename__ = "new_arrivals"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    product = relationship("Product")
