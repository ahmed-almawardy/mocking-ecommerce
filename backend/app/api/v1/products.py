import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_redis
from app.db.session import get_db
from app.models import Product
from app.schemas.products import ProductOut, ProductPage

router = APIRouter(prefix="/products", tags=["catalog"])


@router.get("", response_model=ProductPage)
async def list_products(
    q: str | None = None,
    category: str | None = None,
    featured: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=60),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    cache_material = json.dumps(
        {"q": q, "category": category, "featured": featured, "page": page, "page_size": page_size},
        sort_keys=True, separators=(",", ":"),
    )
    cache_key = f"catalog:products:{hashlib.sha256(cache_material.encode()).hexdigest()}"
    try:
        cached = await redis.get(cache_key)
        if cached:
            return ProductPage.model_validate_json(cached)
    except (RedisError, ValueError):
        pass

    statement = select(Product).where(Product.is_active.is_(True))
    count_statement = select(func.count(Product.id)).where(Product.is_active.is_(True))
    if q:
        term = f"%{q.strip()}%"
        filter_expr = or_(Product.name.ilike(term), Product.description.ilike(term), Product.sku.ilike(term))
        statement = statement.where(filter_expr)
        count_statement = count_statement.where(filter_expr)
    if category:
        statement = statement.where(Product.category.ilike(category.strip()))
        count_statement = count_statement.where(Product.category.ilike(category.strip()))
    if featured is not None:
        statement = statement.where(Product.featured.is_(featured))
        count_statement = count_statement.where(Product.featured.is_(featured))
    total = await db.scalar(count_statement) or 0
    products = (await db.scalars(statement.order_by(Product.featured.desc(), Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size))).all()
    result = ProductPage(items=[ProductOut.model_validate(p) for p in products], total=total, page=page, page_size=page_size)
    try:
        await redis.setex(cache_key, 60, result.model_dump_json())
    except RedisError:
        pass
    return result


@router.get("/categories", response_model=list[str])
async def list_categories(db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    try:
        cached = await redis.get("catalog:categories")
        if cached:
            return json.loads(cached)
    except (RedisError, json.JSONDecodeError):
        pass
    rows = await db.scalars(select(Product.category).where(Product.is_active.is_(True)).distinct().order_by(Product.category))
    result = list(rows.all())
    try:
        await redis.setex("catalog:categories", 300, json.dumps(result))
    except RedisError:
        pass
    return result


@router.get("/{slug}", response_model=ProductOut)
async def get_product(slug: str, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    cache_key = f"catalog:product:{slug}"
    try:
        cached = await redis.get(cache_key)
        if cached:
            return ProductOut.model_validate_json(cached)
    except (RedisError, ValueError):
        pass
    product = await db.scalar(select(Product).where(Product.slug == slug, Product.is_active.is_(True)))
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    result = ProductOut.model_validate(product)
    try:
        await redis.setex(cache_key, 120, result.model_dump_json())
    except RedisError:
        pass
    return result
