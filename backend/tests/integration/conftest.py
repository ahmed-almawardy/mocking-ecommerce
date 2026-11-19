"""Shared real-PostgreSQL fixture for CI and local integration runs."""

import os
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models import AuthIdentity, Offer, Order, OrderItem, PaymentTransaction, Product, ProductEvent, User  # noqa: F401


@pytest_asyncio.fixture
async def postgres_sessions() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Set TEST_DATABASE_URL to run real PostgreSQL integration tests")

    parsed_url = make_url(database_url)
    if not parsed_url.database or not parsed_url.database.endswith("_test"):
        raise RuntimeError(
            "TEST_DATABASE_URL must point to a dedicated database whose name ends in '_test'; "
            "the integration fixture truncates test tables."
        )

    engine = create_async_engine(parsed_url, pool_pre_ping=True)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await connection.execute(
            text(
                "TRUNCATE TABLE payment_transactions, product_events, offers, order_items, orders, products, auth_identities, users "
                "RESTART IDENTITY CASCADE"
            )
        )
    try:
        yield session_factory
    finally:
        async with engine.begin() as connection:
            await connection.execute(
                text(
                    "TRUNCATE TABLE payment_transactions, product_events, offers, order_items, orders, products, auth_identities, users "
                    "RESTART IDENTITY CASCADE"
                )
            )
        await engine.dispose()
