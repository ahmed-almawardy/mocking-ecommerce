"""HTTP-level checkout tests with external payment provider isolated by a fake."""

from collections.abc import AsyncIterator
from decimal import Decimal
from uuid import uuid4

import httpx
import pytest

from app.models import Order, OrderItem, Product



class Rows:
    def __init__(self, values):
        self.values = values

    def all(self):
        return self.values


class CheckoutDB:
    def __init__(self, product: Product) -> None:
        self.product = product
        self.added: list[object] = []

    async def scalars(self, statement):
        return Rows([self.product])

    def add(self, value: object) -> None:
        self.added.append(value)

    async def flush(self) -> None:
        for value in self.added:
            if isinstance(value, Order) and value.id is None:
                value.id = uuid4()

    async def commit(self) -> None:
        return None


@pytest.mark.asyncio
async def test_checkout_uses_database_price_and_merges_duplicate_cart_lines(monkeypatch) -> None:
    pytest.importorskip("redis", reason="Install backend/requirements.txt to run API integration tests")
    pytest.importorskip("authlib", reason="Install backend/requirements.txt to run API integration tests")
    from app.api.deps import get_current_user
    from app.db.session import get_db
    from app.main import app

    product_id = uuid4()
    product = Product(
        id=product_id, sku="NH-TEST-ORDER", slug="test-order-product", name="Test Product",
        category="Cookers", description="Test description", price=Decimal("500.00"),
        compare_at_price=None, stock_qty=5, image_url="/test.webp", badge=None,
        featured=False, is_active=True,
    )
    db = CheckoutDB(product)
    user = type("TestUser", (), {"id": uuid4(), "email": "shopper@example.com"})()
    payment_arguments: dict[str, object] = {}

    async def override_db() -> AsyncIterator[CheckoutDB]:
        yield db

    async def override_user():
        return user

    async def fake_payment_session(**kwargs):
        payment_arguments.update(kwargs)
        return "https://payments.example.test/session"

    monkeypatch.setattr("app.api.v1.orders.create_payment_session", fake_payment_session)
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/orders",
                json={
                    "items": [
                        {"product_id": str(product_id), "quantity": 1},
                        {"product_id": str(product_id), "quantity": 1},
                    ],
                    "shipping_name": "Test Shopper",
                    "shipping_phone": "+201012345678",
                    "shipping_address": "12 Example Street, apartment 4",
                    "shipping_city": "Giza",
                },
            )

        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["subtotal"] == "1000.00"
        assert payload["shipping_fee"] == "75.00"
        assert payload["total"] == "1075.00"
        assert payload["payment_url"] == "https://payments.example.test/session"
        order = next(value for value in db.added if isinstance(value, Order))
        assert order.payment_status == "pending"
        order_items = [value for value in db.added if isinstance(value, OrderItem)]
        assert len(order_items) == 1
        assert order_items[0].quantity == 2
        assert payment_arguments["amount"] == Decimal("1075.00")
        assert product.stock_qty == 5  # Inventory is decremented only after verified payment.
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_checkout_rejects_aggregated_quantity_over_twenty() -> None:
    pytest.importorskip("redis", reason="Install backend/requirements.txt to run API integration tests")
    pytest.importorskip("authlib", reason="Install backend/requirements.txt to run API integration tests")
    from app.api.deps import get_current_user
    from app.db.session import get_db
    from app.main import app

    product_id = uuid4()
    product = Product(
        id=product_id, sku="NH-TEST-LIMIT", slug="test-limit", name="Test Product",
        category="Cookers", description="Test", price=Decimal("10.00"),
        compare_at_price=None, stock_qty=100, image_url="", badge=None,
        featured=False, is_active=True,
    )
    db = CheckoutDB(product)
    user = type("TestUser", (), {"id": uuid4(), "email": "shopper@example.com"})()

    async def override_db() -> AsyncIterator[CheckoutDB]:
        yield db

    async def override_user():
        return user

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/orders",
                json={
                    "items": [
                        {"product_id": str(product_id), "quantity": 11},
                        {"product_id": str(product_id), "quantity": 10},
                    ],
                    "shipping_name": "Test Shopper",
                    "shipping_phone": "+201012345678",
                    "shipping_address": "12 Example Street, apartment 4",
                    "shipping_city": "Giza",
                },
            )
        assert response.status_code == 422
        assert "cannot exceed 20" in response.json()["detail"]
        assert db.added == []
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)
