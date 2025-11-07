from __future__ import annotations

from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from .db import SessionLocal
from .schemas import (
    ScrapeRequest,
    ProductsResponse,
    ProductOut,
)
from .services import (
    run_scrape,
    persist_scrape_results,
    fetch_products,
    export_products_csv,
)

router = APIRouter()


# --- DB dependency (local to this router) ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- Endpoints ---

@router.post("/scrape")
def post_scrape(req: ScrapeRequest, db: Session = Depends(get_db)):
    try:
        items = run_scrape(req)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Scrape failed: {e!s}")
    changed = persist_scrape_results(db, items)
    return {"fetched": len(items), "inserted_or_updated": changed}


@router.get("/products", response_model=ProductsResponse)
def products(
    q: str | None = Query(None),
    min_rating: float | None = Query(None),
    max_price: float | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    order_by: str = Query("created_at", pattern="^(price|rating|created_at|updated_at|title)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    rows, total = fetch_products(
        db,
        q=q,
        min_rating=min_rating,
        max_price=max_price,
        page=page,
        page_size=page_size,
        order_by=order_by,
        order=order,
    )
    return ProductsResponse(
        page=page,
        page_size=page_size,
        total=total,
        items=[ProductOut.model_validate(r) for r in rows],
    )


@router.get("/products.csv", response_class=PlainTextResponse)
def products_csv(
    q: str | None = Query(None),
    min_rating: float | None = Query(None),
    max_price: float | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(1000, ge=1, le=5000),
    order_by: str = Query("created_at", pattern="^(price|rating|created_at|updated_at|title)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    return export_products_csv(
        db,
        q=q,
        min_rating=min_rating,
        max_price=max_price,
        page=page,
        page_size=page_size,
        order_by=order_by,
        order=order,
    )
