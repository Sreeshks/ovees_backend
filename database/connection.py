from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ovees.db")

# Create engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize database
def init_db():
    from models import Product, Category, Combo, ComboProduct, NewArrival, Admin, Banner
    Base.metadata.create_all(bind=engine)

    # Ensure new columns exist for Category (safe for existing sqlite DBs)
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            res = conn.execute(text("PRAGMA table_info(categories)"))
            existing_cols = [row[1] for row in res.fetchall()]
            if 'icon_url' not in existing_cols:
                try:
                    conn.execute(text("ALTER TABLE categories ADD COLUMN icon_url VARCHAR"))
                except Exception:
                    pass
            if 'icon_public_id' not in existing_cols:
                try:
                    conn.execute(text("ALTER TABLE categories ADD COLUMN icon_public_id VARCHAR"))
                except Exception:
                    pass
    except Exception:
        # If the table does not exist or any error occurs, skip - create_all above will handle new DBs
        pass
