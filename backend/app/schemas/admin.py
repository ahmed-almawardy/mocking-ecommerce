from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from decimal import Decimal

from fastapi import HTTPException
from pydantic import BaseModel, Field, model_validator


def utc_bounds(start: date, end: date) -> tuple[datetime, datetime]:
    if end < start:
        raise HTTPException(status_code=422, detail="The end date must be on or after the start date")
    if (end - start).days > 366:
        raise HTTPException(status_code=422, detail="Analytics date range cannot exceed 367 days")
    # Store reporting dates follow the storefront's Egyptian local calendar.
    # Convert local midnight boundaries to UTC for timestamptz comparisons.
    cairo = ZoneInfo("Africa/Cairo")
    start_local = datetime.combine(start, time.min, tzinfo=cairo)
    end_local = datetime.combine(end + timedelta(days=1), time.min, tzinfo=cairo)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


class ProductCreate(BaseModel):
    sku: str = Field(min_length=2, max_length=80)
    slug: str = Field(min_length=2, max_length=180, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str = Field(min_length=2, max_length=220)
    category: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=10000)
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    compare_at_price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    stock_qty: int = Field(default=0, ge=0, le=1000000)
    image_url: str = Field(min_length=1, max_length=700)
    badge: str | None = Field(default=None, max_length=50)
    featured: bool = False
    is_active: bool = True


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=2, max_length=80)
    slug: str | None = Field(default=None, min_length=2, max_length=180, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    name: str | None = Field(default=None, min_length=2, max_length=220)
    category: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=10000)
    price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    compare_at_price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    stock_qty: int | None = Field(default=None, ge=0, le=1000000)
    image_url: str | None = Field(default=None, min_length=1, max_length=700)
    badge: str | None = Field(default=None, max_length=50)
    featured: bool | None = None
    is_active: bool | None = None


class OfferCreate(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    subtitle: str = Field(default="", max_length=300)
    title_ar: str | None = Field(default=None, max_length=180)
    subtitle_ar: str | None = Field(default=None, max_length=300)
    image_url: str = Field(min_length=1, max_length=700)
    link_url: str = Field(default="/en/products", max_length=700)
    badge: str | None = Field(default=None, max_length=60)
    is_active: bool = True
    sort_order: int = Field(default=0, ge=0, le=10000)
    starts_at: datetime | None = None
    ends_at: datetime | None = None

    @model_validator(mode="after")
    def dates_are_ordered(self):
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValueError("Offer end time must be later than its start time")
        return self


class OfferUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=180)
    subtitle: str | None = Field(default=None, max_length=300)
    title_ar: str | None = Field(default=None, max_length=180)
    subtitle_ar: str | None = Field(default=None, max_length=300)
    image_url: str | None = Field(default=None, min_length=1, max_length=700)
    link_url: str | None = Field(default=None, max_length=700)
    badge: str | None = Field(default=None, max_length=60)
    is_active: bool | None = None
    sort_order: int | None = Field(default=None, ge=0, le=10000)
    starts_at: datetime | None = None
    ends_at: datetime | None = None

    @model_validator(mode="after")
    def dates_are_ordered(self):
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValueError("Offer end time must be later than its start time")
        return self

