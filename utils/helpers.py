from typing import Optional


def filter_by_price_range(price: float, min_price: Optional[float], max_price: Optional[float]) -> bool:
    """Check if price is within the given range"""
    if min_price is not None and price < min_price:
        return False
    if max_price is not None and price > max_price:
        return False
    return True


def recompute_and_update_combo_prices(db, combo):
    """Recompute normal_price and total_price for a given Combo SQLAlchemy instance and persist changes.

    Uses product.offer_price when available for effective price, otherwise normal_price.
    Returns (normal_sum, effective_sum)
    """
    try:
        from models import ComboProduct, Product
        # Fetch joined product data for this combo
        rows = db.query(Product.normal_price, Product.offer_price, ComboProduct.quantity).join(ComboProduct, ComboProduct.product_id == Product.id).filter(ComboProduct.combo_id == combo.id).all()
        normal_sum = 0.0
        effective_sum = 0.0
        for nr in rows:
            np = float(nr[0] or 0.0)
            op = nr[1]
            qty = int(nr[2] or 1)
            eff = float(op) if (op is not None) else np
            normal_sum += np * qty
            effective_sum += eff * qty

        combo.normal_price = normal_sum
        combo.total_price = effective_sum
        db.add(combo)
        db.commit()
        db.refresh(combo)
        return normal_sum, effective_sum
    except Exception:
        # if anything goes wrong, roll back and ignore (don't break reads)
        try:
            db.rollback()
        except Exception:
            pass
        return 0.0, 0.0
