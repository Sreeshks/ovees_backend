from typing import Optional


def filter_by_price_range(price: float, min_price: Optional[float], max_price: Optional[float]) -> bool:
    """Check if price is within the given range"""
    if min_price is not None and price < min_price:
        return False
    if max_price is not None and price > max_price:
        return False
    return True
