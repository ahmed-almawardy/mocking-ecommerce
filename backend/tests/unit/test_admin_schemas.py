import pytest
from pydantic import ValidationError

from app.schemas.admin import OfferCreate, ProductCreate, utc_bounds


def test_product_create_requires_positive_price_and_valid_slug():
    payload = {
        "sku": "NH-TEST-001", "slug": "nova-test-product", "name": "Test product",
        "category": "Small Home Appliances", "price": "1200.00", "image_url": "/images/products/blender.webp",
    }
    assert ProductCreate(**payload).price == 1200
    with pytest.raises(ValidationError):
        ProductCreate(**{**payload, "price": "0"})
    with pytest.raises(ValidationError):
        ProductCreate(**{**payload, "slug": "Invalid Slug"})


def test_offer_create_rejects_end_before_start():
    with pytest.raises(ValidationError):
        OfferCreate(
            title="Winter offers", image_url="/images/offers/offer-1.webp",
            starts_at="2026-11-20T12:00:00Z", ends_at="2026-11-19T12:00:00Z",
        )


def test_analytics_range_uses_egypt_local_midnight_and_exclusive_next_day():
    from datetime import date, datetime, timezone

    start, end = utc_bounds(date(2026, 11, 1), date(2026, 11, 16))
    # Cairo is UTC+2 in November 2026, so local midnight is 22:00 UTC on the prior day.
    assert start == datetime(2026, 10, 31, 22, 0, tzinfo=timezone.utc)
    assert end == datetime(2026, 11, 16, 22, 0, tzinfo=timezone.utc)
    with pytest.raises(Exception):
        utc_bounds(date(2026, 11, 17), date(2026, 11, 16))
