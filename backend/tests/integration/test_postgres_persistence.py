"""End-to-end API-to-PostgreSQL persistence tests (enabled in CI)."""

from collections.abc import AsyncIterator
from decimal import Decimal
from uuid import uuid4

import httpx
import pytest
from sqlalchemy import func, select


@pytest.mark.asyncio
async def test_registration_persists_user_and_normalized_egyptian_phone(postgres_sessions) -> None:
    pytest.importorskip("redis", reason="Install backend/requirements.txt to run API integration tests")
    pytest.importorskip("authlib", reason="Install backend/requirements.txt to run API integration tests")
    from app.db.session import get_db
    from app.main import app
    from app.models import User

    async def override_db() -> AsyncIterator:
        async with postgres_sessions() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "name": "Postgres Shopper",
                    "email": "pg-shopper@example.com",
                    "phone": "010 1234 5678",
                    "password": "A-Strong-Postgres-Password-2026",
                    "whatsapp_opt_in": False,
                },
            )
        assert response.status_code == 201, response.text
        assert response.json()["user"]["phone"] == "+201012345678"
        async with postgres_sessions() as session:
            user = await session.scalar(select(User).where(User.email == "pg-shopper@example.com"))
            total = await session.scalar(select(func.count(User.id)))
        assert user is not None
        assert user.password_hash != "A-Strong-Postgres-Password-2026"
        assert total == 1
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_order_api_persists_order_and_items_using_postgres_price(postgres_sessions, monkeypatch) -> None:
    pytest.importorskip("redis", reason="Install backend/requirements.txt to run API integration tests")
    pytest.importorskip("authlib", reason="Install backend/requirements.txt to run API integration tests")
    from app.api.deps import get_current_user
    from app.db.session import get_db
    from app.main import app
    from app.models import Order, OrderItem, Product, User

    user = User(
        id=uuid4(), name="Checkout Shopper", email="checkout@example.com",
        phone="+201012345678", password_hash=None,
    )
    product = Product(
        id=uuid4(), sku="NH-PG-001", slug="postgres-product", name="Postgres Product",
        category="Cookers", description="Database-backed test product", price=Decimal("500.00"),
        compare_at_price=None, stock_qty=5, image_url="/test.webp", badge=None,
        featured=False, is_active=True,
    )
    async with postgres_sessions() as session:
        session.add_all([user, product])
        await session.commit()

    async def override_db() -> AsyncIterator:
        async with postgres_sessions() as session:
            yield session

    async def override_user():
        return user

    async def fake_payment_session(**kwargs):
        assert kwargs["amount"] == Decimal("1075.00")
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
                        {"product_id": str(product.id), "quantity": 1},
                        {"product_id": str(product.id), "quantity": 1},
                    ],
                    "shipping_name": "Checkout Shopper",
                    "shipping_phone": "+201012345678",
                    "shipping_address": "12 Example Street, apartment 4",
                    "shipping_city": "Giza",
                },
            )
        assert response.status_code == 200, response.text
        assert response.json()["total"] == "1075.00"
        async with postgres_sessions() as session:
            order = await session.scalar(select(Order).where(Order.order_number == response.json()["order_number"]))
            assert order is not None
            items = list((await session.scalars(select(OrderItem).where(OrderItem.order_id == order.id))).all())
            stored_product = await session.get(Product, product.id)
        assert order.payment_status == "pending"
        assert len(items) == 1
        assert items[0].quantity == 2
        assert stored_product is not None
        assert stored_product.stock_qty == 5
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)
