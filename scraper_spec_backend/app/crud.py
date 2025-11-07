from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc, asc
from .models import Product, PriceHistory

def _extract_currency(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    s = raw.upper()
    if "AED" in s: return "AED" # noqa: E701
    if "USD" in s: return "USD"# noqa: E701
    if "EUR" in s or "€" in s: return "EUR"  # noqa: E701
    if "GBP" in s or "£" in s: return "GBP"# noqa: E701
    if "$" in raw and "USD" not in s: return "USD"# noqa: E701
    if "SAR" in s: return "SAR"# noqa: E701
    return None

def upsert_products(db: Session, items: List[dict]) -> int:
    """
    Upsert by ASIN. If price changed, append a price_history row.
    Accepts optional fields: price_raw, currency, rating_count.
    """
    changed = 0
    for it in items:
        asin = (it.get("asin") or "").strip()
        if not asin:
            continue

        existing = db.execute(select(Product).where(Product.asin == asin)).scalar_one_or_none()

        price = it.get("price")
        price_raw = it.get("price_raw")
        currency = it.get("currency") or _extract_currency(price_raw or "")

        if existing:
            dirty = False
            for fld, val in [
                ("title", it.get("title")),
                ("product_url", it.get("product_url")),
                ("image_url", it.get("image_url")),
                ("price", price),
                ("price_raw", price_raw),
                ("currency", currency),
                ("rating", it.get("rating")),
                ("rating_count", it.get("rating_count")),
            ]:
                if val is not None and getattr(existing, fld) != val:
                    setattr(existing, fld, val) 
                    dirty = True

            # price history
            if price is not None:
                last = db.execute(
                    select(PriceHistory).where(PriceHistory.asin == asin).order_by(PriceHistory.seen_at.desc())
                ).scalars().first()
                if last is None or last.price != price:
                    db.add(PriceHistory(asin=asin, price=price, price_raw=price_raw, currency=currency))
            if dirty:
                changed += 1
        else:
            db.add(Product(
                asin=asin,
                title=it.get("title",""),
                product_url=it.get("product_url",""),
                image_url=it.get("image_url"),
                price=price,
                price_raw=price_raw,
                currency=currency,
                rating=it.get("rating"),
                rating_count=it.get("rating_count"),
            ))
            if price is not None:
                db.add(PriceHistory(asin=asin, price=price, price_raw=price_raw, currency=currency))
            changed += 1

    db.commit()
    return changed

def list_products(
    db: Session,
    q: Optional[str],
    min_rating: Optional[float],
    max_price: Optional[float],
    page: int,
    page_size: int,
    order_by: str,
    order: str,
) -> Tuple[List[Product], int]:
    stmt = select(Product)
    if q:
        stmt = stmt.filter(Product.title.ilike(f"%{q}%"))
    if min_rating is not None:
        stmt = stmt.filter(Product.rating >= min_rating)
    if max_price is not None:
        stmt = stmt.filter(Product.price <= max_price)

    total = db.execute(select(func.count()).select_from(stmt.subquery())).scalar_one()

    colmap = {
        "price": Product.price,
        "rating": Product.rating,
        "created_at": Product.created_at,
        "updated_at": Product.updated_at,
        "title": Product.title,
    }
    col = colmap.get(order_by, Product.created_at)
    stmt = stmt.order_by(asc(col) if order == "asc" else desc(col))

    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    items = db.execute(stmt).scalars().all()
    return items, total

def get_history(db: Session, asin: str, limit: int = 200) -> List[PriceHistory]:
    stmt = (
        select(PriceHistory)
        .where(PriceHistory.asin == asin)
        .order_by(PriceHistory.seen_at.asc())
        .limit(limit)
    )
    return db.execute(stmt).scalars().all()
