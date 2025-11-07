from __future__ import annotations
from typing import List, Tuple
from sqlalchemy.orm import Session

from .schemas import ScrapeRequest
from .scraper import scrape_via_browser, scrape_by_url
from .crud import upsert_products, list_products, get_history


# ---------- Scrape orchestration ----------

def run_scrape(req: ScrapeRequest) -> List[dict]:
    """Run a scrape using either keyword or full search URL."""
    if req.keyword:
        return scrape_via_browser(
            keyword=req.keyword,
            domain=req.domain,
            max_pages=req.max_pages,
            delay=(req.delay_lo, req.delay_hi),
        )
    return scrape_by_url(
        search_url=str(req.search_url),
        max_pages=req.max_pages,
        delay=(req.delay_lo, req.delay_hi),
    )


def persist_scrape_results(db: Session, items: List[dict]) -> int:
    """Upsert products and return # of inserted/updated rows."""
    return upsert_products(db, items)


# ---------- Query helpers ----------

def fetch_products(
    db: Session,
    *,
    q: str | None,
    min_rating: float | None,
    max_price: float | None,
    page: int,
    page_size: int,
    order_by: str,
    order: str,
) -> Tuple[list, int]:
    """Return (rows, total)."""
    return list_products(
        db,
        q=q,
        min_rating=min_rating,
        max_price=max_price,
        page=page,
        page_size=page_size,
        order_by=order_by,
        order=order,
    )


def export_products_csv(
    db: Session,
    *,
    q: str | None,
    min_rating: float | None,
    max_price: float | None,
    page: int,
    page_size: int,
    order_by: str,
    order: str,
) -> str:
    """Return CSV text for the selected products."""
    rows, _ = fetch_products(
        db,
        q=q,
        min_rating=min_rating,
        max_price=max_price,
        page=page,
        page_size=page_size,
        order_by=order_by,
        order=order,
    )

    cols = [
        "asin", "title", "product_url", "image_url",
        "price", "price_raw", "currency",
        "rating", "rating_count",
        "created_at", "updated_at",
    ]
    lines = [",".join(cols)]
    for r in rows:
        # keep CSV simple; strip commas from fields
        row = [str(getattr(r, c) or "").replace(",", " ") for c in cols]
        lines.append(",".join(row))
    return "\n".join(lines)


def fetch_history_points(db: Session, asin: str, limit: int = 500):
    """Return price-history ORM rows for an ASIN."""
    return get_history(db, asin, limit=limit)
