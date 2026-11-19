import pytest

from app.services.catalog_cache import invalidate_catalog_cache


class FakeRedis:
    def __init__(self, keys):
        self.keys = keys
        self.deleted = []

    async def scan_iter(self, match, count):
        assert match == "catalog:*"
        assert count == 200
        for key in self.keys:
            if key.startswith("catalog:"):
                yield key

    async def delete(self, *keys):
        self.deleted.extend(keys)


@pytest.mark.asyncio
async def test_catalog_invalidation_deletes_only_catalog_keys():
    redis = FakeRedis(["catalog:categories", "catalog:product:blender", "other:key"])
    await invalidate_catalog_cache(redis)
    assert redis.deleted == ["catalog:categories", "catalog:product:blender"]


@pytest.mark.asyncio
async def test_catalog_invalidation_is_best_effort_when_redis_is_unavailable():
    class UnavailableRedis:
        async def scan_iter(self, **kwargs):
            raise OSError("Redis is unavailable")
            yield  # pragma: no cover

    await invalidate_catalog_cache(UnavailableRedis())
