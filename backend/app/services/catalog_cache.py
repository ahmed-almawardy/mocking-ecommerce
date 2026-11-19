"""Best-effort invalidation for cached public catalog responses."""

from __future__ import annotations

from typing import Any



async def invalidate_catalog_cache(redis: Any) -> None:
    """Delete cached catalog lists, categories and product-detail documents.

    Admin writes must remain successful if Redis is temporarily unavailable;
    the short TTL is the fallback consistency mechanism in that case.
    """
    try:
        keys = [key async for key in redis.scan_iter(match="catalog:*", count=200)]
        if keys:
            await redis.delete(*keys)
    except Exception:
        return
