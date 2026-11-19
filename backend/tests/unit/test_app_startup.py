"""Regression tests for app-level middleware imports and wiring."""

import pytest

from starlette.middleware.sessions import SessionMiddleware


def test_starlette_session_middleware_imports_with_signing_support() -> None:
    """Importing this middleware requires the itsdangerous runtime dependency."""
    assert SessionMiddleware.__name__ == "SessionMiddleware"


def test_session_middleware_is_registered_for_oauth_state() -> None:
    """Authlib's OAuth state validation needs signed Starlette sessions."""
    pytest.importorskip("redis", reason="Install backend/requirements.txt to run app startup tests")
    pytest.importorskip("authlib", reason="Install backend/requirements.txt to run app startup tests")
    from app.main import app

    assert any(middleware.cls is SessionMiddleware for middleware in app.user_middleware)

