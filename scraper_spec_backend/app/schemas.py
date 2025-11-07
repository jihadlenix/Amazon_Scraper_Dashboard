from pydantic import BaseModel, Field, HttpUrl, model_validator
from typing import Optional, List
from datetime import datetime

class ScrapeRequest(BaseModel):
    keyword: Optional[str] = Field(default=None, min_length=1)
    search_url: Optional[HttpUrl] = None
    domain: str = "amazon.com"
    max_pages: int = Field(default=1, ge=1, le=10)
    delay_lo: float = Field(default=2.5, ge=0)
    delay_hi: float = Field(default=5.0, ge=0)

    @model_validator(mode="after")
    def xor_inputs(self):
        if bool(self.keyword) == bool(self.search_url):
            raise ValueError("Provide exactly one of keyword or search_url.")
        return self

class ProductOut(BaseModel):
    id: int
    asin: str
    title: str
    product_url: str
    image_url: Optional[str] = None
    price: Optional[float] = None
    price_raw: Optional[str] = None
    currency: Optional[str] = None
    rating: Optional[float] = None
    rating_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class ProductsResponse(BaseModel):
    page: int
    page_size: int
    total: int
    items: List[ProductOut]

class PricePoint(BaseModel):
    price: Optional[float]
    price_raw: Optional[str]
    currency: Optional[str]
    seen_at: datetime

class HistoryResponse(BaseModel):
    asin: str
    count: int
    points: List[PricePoint]
