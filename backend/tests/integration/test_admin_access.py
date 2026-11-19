from datetime import UTC, datetime
from zoneinfo import ZoneInfo
from uuid import uuid4

import httpx
import pytest

from app.models import User


@pytest.mark.asyncio
async def test_customer_cannot_access_admin_analytics():
    pytest.importorskip("redis")
    pytest.importorskip("authlib")
    from app.api.deps import get_current_user
    from app.main import app

    customer = User(id=uuid4(), name="Ordinary Customer", email="customer@example.com", role="customer", is_active=True, created_at=datetime.now(UTC))
    async def return_customer():
        return customer

    app.dependency_overrides[get_current_user] = return_customer
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/admin/analytics", params={"start":"2026-11-01", "end":"2026-11-16"})
        assert response.status_code == 403
        assert response.json()["detail"] == "Administrator access is required"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_admin_router_requires_authenticated_user():
    pytest.importorskip("redis")
    pytest.importorskip("authlib")
    from app.main import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/admin/products")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_admin_can_read_real_store_analytics(postgres_sessions):
    pytest.importorskip("redis")
    pytest.importorskip("authlib")
    from app.api.deps import get_current_user
    from app.db.session import get_db
    from app.main import app
    from app.models import Order, OrderItem, PaymentTransaction, Product, ProductEvent

    now = datetime.now(UTC)
    cairo_today = datetime.now(ZoneInfo("Africa/Cairo")).date()
    admin = User(id=uuid4(), name="Store Admin", email="admin@example.com", role="admin", is_active=True, created_at=now)
    customer = User(id=uuid4(), name="Test Customer", email="buyer@example.com", role="customer", is_active=True, created_at=now)

    async with postgres_sessions() as db:
        db.add_all([admin, customer])
        await db.flush()
        product = Product(
            sku="NH-ANALYTICS-01", slug="analytics-test-product", name="Analytics Test Product",
            category="Small Home Appliances", description="Integration fixture", price=1000,
            stock_qty=10, image_url="/images/products/blender.webp", is_active=True,
        )
        db.add(product)
        await db.flush()
        order = Order(
            order_number="NH-ANALYTICS-TEST", user_id=customer.id, status="processing", payment_status="paid",
            subtotal=2000, shipping_fee=0, total=2000, currency="EGP", shipping_name="Test Customer",
            shipping_phone="+201000000000", shipping_address="Test address", shipping_city="Cairo",
            payment_provider="kashier", created_at=now,
        )
        db.add(order)
        await db.flush()
        db.add_all([
            OrderItem(order_id=order.id, product_id=product.id, product_name=product.name, sku=product.sku,
                     quantity=2, unit_price=1000, line_total=2000),
            PaymentTransaction(order_id=order.id, provider="kashier", status="paid", amount=2000, currency="EGP", method="card"),
            ProductEvent(product_id=product.id, event_type="view", quantity=1, session_key="integration-session-01"),
            ProductEvent(product_id=product.id, event_type="add_to_cart", quantity=2, session_key="integration-session-01"),
        ])
        await db.commit()

    async def return_admin():
        return admin

    async def override_db():
        async with postgres_sessions() as session:
            yield session

    app.dependency_overrides[get_current_user] = return_admin
    app.dependency_overrides[get_db] = override_db
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/admin/analytics",
                params={"start": cairo_today.isoformat(), "end": cairo_today.isoformat(), "group_by": "day"},
            )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["summary"]["revenue"] == "2000.00"
        assert data["summary"]["paid_orders"] == 1
        assert data["top_selling_products"][0]["units_sold"] == 2
        assert data["most_viewed_products"][0]["views"] == 1
        assert data["most_added_to_cart"][0]["quantity"] == 2
        assert data["payment_distribution"][0]["status"] == "paid"
        assert data["payment_distribution"][0]["amount"] == "2000.00"
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_admin_media_upload_accepts_png_and_rejects_svg(tmp_path, monkeypatch):
    pytest.importorskip("redis")
    pytest.importorskip("authlib")
    pytest.importorskip("multipart")
    from types import SimpleNamespace

    import app.api.v1.admin as admin_module
    from app.api.deps import get_current_user
    from app.main import app

    admin = User(
        id=uuid4(), name="Media Admin", email="media-admin@example.com",
        role="admin", is_active=True, created_at=datetime.now(UTC),
    )

    async def return_admin():
        return admin

    monkeypatch.setattr(admin_module, "get_settings", lambda: SimpleNamespace(media_dir=tmp_path))
    app.dependency_overrides[get_current_user] = return_admin
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            valid_png = b"\x89PNG\r\n\x1a\n" + (b"test-png-data" * 4)
            uploaded = await client.post(
                "/api/v1/admin/media",
                files={"file": ("banner.png", valid_png, "image/png")},
            )
            assert uploaded.status_code == 201, uploaded.text
            result = uploaded.json()
            assert result["url"].startswith("/media/")
            assert result["content_type"] == "image/png"
            assert (tmp_path / result["filename"]).read_bytes() == valid_png

            rejected = await client.post(
                "/api/v1/admin/media",
                files={"file": ("banner.svg", b"<svg></svg>", "image/svg+xml")},
            )
            assert rejected.status_code == 415
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_admin_can_create_product_and_scheduled_offer(postgres_sessions):
    pytest.importorskip("redis")
    pytest.importorskip("authlib")
    from app.api.deps import get_current_user, get_redis
    from app.db.session import get_db
    from app.main import app

    class RedisStub:
        async def scan_iter(self, **kwargs):
            if False:
                yield None

        async def delete(self, *keys):
            return len(keys)

    async def return_redis():
        yield RedisStub()

    admin = User(
        id=uuid4(), name="Catalog Admin", email="catalog-admin@example.com",
        role="admin", is_active=True, created_at=datetime.now(UTC),
    )

    async def return_admin():
        return admin

    async def override_db():
        async with postgres_sessions() as session:
            yield session

    app.dependency_overrides[get_current_user] = return_admin
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_redis] = return_redis
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            product_response = await client.post("/api/v1/admin/products", json={
                "sku": "NH-ADMIN-TEST-01", "slug": "admin-test-product", "name": "Admin Test Product",
                "category": "Small Home Appliances", "description": "Created by the admin integration test",
                "price": "1499.00", "compare_at_price": "1699.00", "stock_qty": 5,
                "image_url": "/images/products/blender.webp", "featured": True, "is_active": True,
            })
            assert product_response.status_code == 201, product_response.text
            product = product_response.json()
            assert product["sku"] == "NH-ADMIN-TEST-01"

            offer_response = await client.post("/api/v1/admin/offers", json={
                "title": "Integration Test Offer", "subtitle": "Admin-created campaign",
                "title_ar": "عرض تجريبي", "subtitle_ar": "حملة أنشأها المسؤول",
                "image_url": "/images/offers/offer-1.webp", "link_url": "/en/products",
                "is_active": True, "sort_order": 9,
                "starts_at": "2026-11-16T00:00:00Z", "ends_at": "2026-12-01T00:00:00Z",
            })
            assert offer_response.status_code == 201, offer_response.text
            offer = offer_response.json()
            assert offer["title_ar"] == "عرض تجريبي"

            product_list = await client.get("/api/v1/admin/products", params={"q": "NH-ADMIN-TEST-01"})
            assert product_list.status_code == 200
            assert product_list.json()["total"] == 1
            offer_list = await client.get("/api/v1/admin/offers")
            assert offer_list.status_code == 200
            assert any(row["id"] == offer["id"] for row in offer_list.json()["items"])
    finally:
        app.dependency_overrides.pop(get_current_user, None)
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_redis, None)
