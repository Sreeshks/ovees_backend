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
            # Ensure combos table has normal_price and total_price columns (safe for sqlite)
            try:
                res2 = conn.execute(text("PRAGMA table_info(combos)"))
                combo_cols = [row[1] for row in res2.fetchall()]
            except Exception:
                combo_cols = []

            if 'normal_price' not in combo_cols:
                try:
                    conn.execute(text("ALTER TABLE combos ADD COLUMN normal_price FLOAT DEFAULT 0.0"))
                except Exception:
                    pass
            if 'total_price' not in combo_cols:
                try:
                    conn.execute(text("ALTER TABLE combos ADD COLUMN total_price FLOAT DEFAULT 0.0"))
                except Exception:
                    pass

            # Recompute and populate totals for existing combos based on combo_products and products
            try:
                combo_ids = [r[0] for r in conn.execute(text("SELECT id FROM combos")).fetchall()]
                for cid in combo_ids:
                    rows = conn.execute(text(
                        "SELECT p.normal_price, p.offer_price, cp.quantity FROM combo_products cp JOIN products p ON cp.product_id = p.id WHERE cp.combo_id = :cid"
                    ), {"cid": cid}).fetchall()
                    normal_sum = 0.0
                    effective_sum = 0.0
                    for nr in rows:
                        np = float(nr[0] or 0.0)
                        op = nr[1]
                        qty = int(nr[2] or 1)
                        eff = float(op) if (op is not None) else np
                        normal_sum += np * qty
                        effective_sum += eff * qty
                    conn.execute(text("UPDATE combos SET normal_price = :np, total_price = :tp WHERE id = :cid"), {"np": normal_sum, "tp": effective_sum, "cid": cid})
            except Exception:
                # If combos table doesn't exist yet or any issue, skip population
                pass
    except Exception:
        # If the table does not exist or any error occurs, skip - create_all above will handle new DBs
        pass
