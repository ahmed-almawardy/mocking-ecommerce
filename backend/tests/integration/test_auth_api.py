"""HTTP-level authentication tests with an isolated AsyncSession substitute."""

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import uuid4

import httpx
import pytest

from app.models import User



class MemoryAuthDB:
    def __init__(self) -> None:
        self.users: list[User] = []
        self.pending: list[object] = []

    async def scalar(self, statement):
        entity = statement.column_descriptions[0]["entity"]
        if entity is User and self.users:
            # These tests issue a single-user registration/login sequence.
            return self.users[0]
        return None

    def add(self, value: object) -> None:
        self.pending.append(value)

    async def commit(self) -> None:
        for value in self.pending:
            if isinstance(value, User) and value not in self.users:
                self.users.append(value)
                value.id = value.id or uuid4()
                value.is_active = True
                value.email_verified = bool(value.email_verified)
                value.whatsapp_opt_in = bool(value.whatsapp_opt_in)
                value.created_at = datetime.now(UTC)
        self.pending.clear()

    async def refresh(self, value: User) -> None:
        value.id = value.id or uuid4()
        value.is_active = True
        value.email_verified = bool(value.email_verified)
        value.whatsapp_opt_in = bool(value.whatsapp_opt_in)
        value.created_at = value.created_at or datetime.now(UTC)


@pytest.mark.asyncio
async def test_register_then_login_sets_http_only_session_cookies() -> None:
    pytest.importorskip("redis", reason="Install backend/requirements.txt to run API integration tests")
    pytest.importorskip("authlib", reason="Install backend/requirements.txt to run API integration tests")
    from app.api.deps import get_current_user
    from app.db.session import get_db
    from app.main import app

    db = MemoryAuthDB()

    async def override_db() -> AsyncIterator[MemoryAuthDB]:
        yield db

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides.pop(get_current_user, None)
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            register_response = await client.post(
                "/api/v1/auth/register",
                json={
                    "name": "Test Shopper",
                    "email": "shopper@example.com",
                    "phone": "01012345678",
                    "password": "A-Strong-Test-Password-2026",
                    "whatsapp_opt_in": False,
                },
            )
            assert register_response.status_code == 201, register_response.text
            assert register_response.json()["user"]["email"] == "shopper@example.com"
            assert "access_token" in register_response.cookies
            assert "refresh_token" in register_response.cookies
            assert "httponly" in register_response.headers.get("set-cookie", "").lower()

            login_response = await client.post(
                "/api/v1/auth/login",
                json={"email": "SHOPPER@example.com", "password": "A-Strong-Test-Password-2026"},
            )
            assert login_response.status_code == 200, login_response.text
            assert login_response.json()["message"] == "Welcome back"
            assert "access_token" in login_response.cookies

            invalid_login = await client.post(
                "/api/v1/auth/login",
                json={"email": "shopper@example.com", "password": "incorrect"},
            )
            assert invalid_login.status_code == 401
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_oauth_provider_diagnostics_endpoint_is_public_and_secret_free():
    pytest.importorskip("redis", reason="Install backend/requirements.txt to run OAuth integration tests")
    pytest.importorskip("authlib", reason="Install backend/requirements.txt to run OAuth integration tests")
    from app.main import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/auth/providers")

    assert response.status_code == 200, response.text
    payload = response.json()
    assert set(payload["providers"]) == {"google", "facebook", "apple"}
    assert payload["providers"]["google"]["callback_url"].endswith("/api/v1/auth/google/callback")
    assert "client_secret" not in response.text.lower()
    assert "client_id" not in response.text.lower()


@pytest.mark.asyncio
async def test_oauth_login_returns_actionable_error_when_provider_is_not_configured(monkeypatch):
    pytest.importorskip("redis", reason="Install backend/requirements.txt to run OAuth integration tests")
    pytest.importorskip("authlib", reason="Install backend/requirements.txt to run OAuth integration tests")
    from app.core.oauth import oauth
    from app.main import app

    monkeypatch.setattr(oauth, "create_client", lambda provider: None)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/auth/google/login")

    assert response.status_code == 503
    assert "Add its OAuth client ID and secret" in response.json()["detail"]
