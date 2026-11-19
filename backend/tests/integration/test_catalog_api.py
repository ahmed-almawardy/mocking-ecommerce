"""FastAPI catalog endpoint tests, including the Redis cache path."""

from collections.abc import AsyncIterator
from decimal import Decimal
from uuid import uuid4

import httpx
import pytest

from app.models import Product



class Rows:
    def __init__(self, values):
        self.values = values

    def all(self):
        return self.values


class MemoryRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    async def get(self, key: str):
        return self.values.get(key)

    async def setex(self, key: str, seconds: int, value: str):
        self.values[key] = value


class CatalogDB:
    def __init__(self, product: Product) -> None:
        self.product = product
        self.scalar_calls = 0
        self.scalars_calls = 0

    async def scalar(self, statement):
        self.scalar_calls += 1
        return 1

    async def scalars(self, statement):
        self.scalars_calls += 1
        return Rows([self.product])


@pytest.mark.asyncio
async def test_product_list_http_response_is_cached_in_redis() -> None:
    pytest.importorskip("redis", reason="Install backend/requirements.txt to run API integration tests")
    pytest.importorskip("authlib", reason="Install backend/requirements.txt to run API integration tests")
    from app.api.deps import get_redis
    from app.db.session import get_db
    from app.main import app

    product = Product(
        id=uuid4(), sku="NH-TEST-001", slug="test-kettle", name="Test Kettle",
        category="Small Home Appliances", description="Test product",
        price=Decimal("1250.00"), compare_at_price=Decimal("1499.00"),
        stock_qty=8, image_url="/images/kettle.webp", badge="Test", featured=True,
        is_active=True,
    )
    db = CatalogDB(product)
    redis = MemoryRedis()

    async def override_db() -> AsyncIterator[CatalogDB]:
        yield db

    async def override_redis():
        return redis

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_redis] = override_redis
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            first = await client.get("/api/v1/products?page=1&page_size=12")
            second = await client.get("/api/v1/products?page=1&page_size=12")

        assert first.status_code == 200, first.text
        assert second.status_code == 200, second.text
        assert first.json() == second.json()
        assert first.json()["total"] == 1
        assert first.json()["items"][0]["sku"] == "NH-TEST-001"
        assert db.scalar_calls == 1
        assert db.scalars_calls == 1
        assert len(redis.values) == 1
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_redis, None)
