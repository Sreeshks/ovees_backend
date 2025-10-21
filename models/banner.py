from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database.connection import Base


class Banner(Base):
    __tablename__ = "banners"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    image_url = Column(String, nullable=False)
    public_id = Column(String, nullable=False)  # Cloudinary public_id
    link_url = Column(String, nullable=True)  # Optional link when banner is clicked
    display_order = Column(Integer, default=0, index=True)  # Order of display
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
