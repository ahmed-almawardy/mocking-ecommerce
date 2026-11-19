from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4
from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_redis
from app.db.session import get_db
from app.core.config import get_settings
from app.models import Offer, Order, OrderItem, PaymentTransaction, Product, ProductEvent, User
from app.schemas.admin import OfferCreate, OfferUpdate, ProductCreate, ProductUpdate, utc_bounds
from app.services.media import detect_raster_image
from app.services.catalog_cache import invalidate_catalog_cache

router = APIRouter(prefix="/admin", tags=["admin"])


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role not in {"admin", "super_admin"}:
        raise HTTPException(status_code=403, detail="Administrator access is required")
    return user



def serialize_product(product: Product) -> dict:
    return {
        "id": str(product.id), "sku": product.sku, "slug": product.slug,
        "name": product.name, "category": product.category,
        "description": product.description, "price": str(product.price),
        "compare_at_price": str(product.compare_at_price) if product.compare_at_price is not None else None,
        "stock_qty": product.stock_qty, "image_url": product.image_url,
        "badge": product.badge, "featured": product.featured,
        "is_active": product.is_active,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
    }


def serialize_offer(offer: Offer) -> dict:
    return {
        "id": str(offer.id), "title": offer.title, "subtitle": offer.subtitle,
        "title_ar": offer.title_ar, "subtitle_ar": offer.subtitle_ar, "image_url": offer.image_url, "link_url": offer.link_url, "badge": offer.badge,
        "is_active": offer.is_active, "sort_order": offer.sort_order,
        "starts_at": offer.starts_at.isoformat() if offer.starts_at else None,
        "ends_at": offer.ends_at.isoformat() if offer.ends_at else None,
        "created_at": offer.created_at.isoformat() if offer.created_at else None,
    }


@router.post("/media", status_code=201)
async def upload_admin_media(file: UploadFile = File(...), _: User = Depends(require_admin)):
    """Store a validated raster image and return a same-origin public media URL."""
    maximum_bytes = 10 * 1024 * 1024
    content = await file.read(maximum_bytes + 1)
    await file.close()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded image is empty")
    if len(content) > maximum_bytes:
        raise HTTPException(status_code=413, detail="Image files must be 10 MB or smaller")

    # Validate file signatures rather than trusting the browser-supplied MIME type or extension.
    image_format = detect_raster_image(content)
    if image_format is None:
        raise HTTPException(status_code=415, detail="Upload a valid JPEG, PNG or WebP image")
    extension, media_type = image_format.extension, image_format.content_type

    settings = get_settings()
    directory = Path(settings.media_dir).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.{extension}"
    destination = directory / filename
    destination.write_bytes(content)
    return {"url": f"/media/{filename}", "filename": filename, "content_type": media_type, "size": len(content)}


@router.get("/analytics")
async def dashboard_analytics(
    start: date = Query(...),
    end: date = Query(...),
    group_by: Literal["day", "week", "month"] = "day",
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    start_at, end_at = utc_bounds(start, end)
    order_filter = and_(Order.created_at >= start_at, Order.created_at < end_at)
    user_filter = and_(User.created_at >= start_at, User.created_at < end_at)
    event_filter = and_(ProductEvent.created_at >= start_at, ProductEvent.created_at < end_at)
    # Group on Egypt's local calendar, not the database server's timezone.
    local_order_time = func.timezone("Africa/Cairo", Order.created_at)
    bucket = func.date_trunc(group_by, local_order_time).label("bucket")

    total_orders = await db.scalar(select(func.count(Order.id)).where(order_filter)) or 0
    paid_revenue = await db.scalar(
        select(func.coalesce(func.sum(Order.total), 0)).where(order_filter, Order.payment_status == "paid")
    ) or Decimal("0")
    paid_orders = await db.scalar(
        select(func.count(Order.id)).where(order_filter, Order.payment_status == "paid")
    ) or 0
    pending_payments = await db.scalar(
        select(func.count(Order.id)).where(order_filter, Order.payment_status == "pending")
    ) or 0
    new_customers = await db.scalar(select(func.count(User.id)).where(user_filter, User.role == "customer")) or 0
    total_customers = await db.scalar(select(func.count(User.id)).where(User.role == "customer")) or 0
    active_products = await db.scalar(select(func.count(Product.id)).where(Product.is_active.is_(True))) or 0
    low_stock = await db.scalar(
        select(func.count(Product.id)).where(Product.is_active.is_(True), Product.stock_qty <= 5)
    ) or 0

    revenue_rows = (await db.execute(
        select(bucket, func.coalesce(func.sum(Order.total), 0).label("revenue"), func.count(Order.id).label("orders"))
        .where(order_filter, Order.payment_status == "paid")
        .group_by(bucket).order_by(bucket)
    )).all()

    local_user_time = func.timezone("Africa/Cairo", User.created_at)
    user_bucket = func.date_trunc(group_by, local_user_time).label("bucket")
    user_rows = (await db.execute(
        select(user_bucket, func.count(User.id).label("users"))
        .where(user_filter, User.role == "customer").group_by(user_bucket).order_by(user_bucket)
    )).all()

    # Prefer the payment ledger but retain historical orders created before the
    # ledger migration by falling back to their persisted order payment fields.
    effective_payment_status = func.coalesce(PaymentTransaction.status, Order.payment_status).label("status")
    effective_payment_amount = func.coalesce(PaymentTransaction.amount, Order.total)
    payment_rows = (await db.execute(
        select(effective_payment_status, func.count(Order.id).label("count"),
               func.coalesce(func.sum(effective_payment_amount), 0).label("amount"))
        .select_from(Order)
        .outerjoin(PaymentTransaction, PaymentTransaction.order_id == Order.id)
        .where(order_filter)
        .group_by(effective_payment_status)
        .order_by(effective_payment_status)
    )).all()

    top_selling_rows = (await db.execute(
        select(Product.id, Product.name, Product.image_url,
               func.coalesce(func.sum(OrderItem.quantity), 0).label("units"),
               func.coalesce(func.sum(OrderItem.line_total), 0).label("revenue"))
        .join(OrderItem, OrderItem.product_id == Product.id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(order_filter, Order.payment_status == "paid")
        .group_by(Product.id, Product.name, Product.image_url)
        .order_by(desc("units")).limit(5)
    )).all()

    async def event_rank(event_type: str, metric: str):
        metric_expr = func.sum(ProductEvent.quantity) if metric == "quantity" else func.count(ProductEvent.id)
        return (await db.execute(
            select(Product.id, Product.name, Product.image_url, metric_expr.label("value"))
            .join(ProductEvent, ProductEvent.product_id == Product.id)
            .where(event_filter, ProductEvent.event_type == event_type)
            .group_by(Product.id, Product.name, Product.image_url)
            .order_by(desc("value")).limit(5)
        )).all()

    viewed_rows = await event_rank("view", "count")
    cart_rows = await event_rank("add_to_cart", "quantity")

    recent_rows = (await db.execute(
        select(Order, User.name, User.email)
        .join(User, User.id == Order.user_id)
        .where(order_filter).order_by(Order.created_at.desc()).limit(8)
    )).all()

    return {
        "range": {"start": start.isoformat(), "end": end.isoformat(), "group_by": group_by},
        "summary": {
            "revenue": str(paid_revenue), "orders": int(total_orders), "paid_orders": int(paid_orders),
            "pending_payments": int(pending_payments), "new_customers": int(new_customers),
            "total_customers": int(total_customers), "active_products": int(active_products),
            "low_stock_products": int(low_stock),
        },
        "revenue_series": [
            {"date": row.bucket.isoformat(), "revenue": str(row.revenue), "orders": int(row.orders)}
            for row in revenue_rows
        ],
        "user_series": [{"date": row.bucket.isoformat(), "users": int(row.users)} for row in user_rows],
        "payment_distribution": [
            {"status": row.status, "count": int(row.count), "amount": str(row.amount)}
            for row in payment_rows
        ],
        "top_selling_products": [
            {"id": str(row.id), "name": row.name, "image_url": row.image_url,
             "units_sold": int(row.units), "revenue": str(row.revenue)} for row in top_selling_rows
        ],
        "most_viewed_products": [
            {"id": str(row.id), "name": row.name, "image_url": row.image_url, "views": int(row.value)}
            for row in viewed_rows
        ],
        "most_added_to_cart": [
            {"id": str(row.id), "name": row.name, "image_url": row.image_url, "quantity": int(row.value)}
            for row in cart_rows
        ],
        "recent_orders": [
            {"order_number": order.order_number, "customer_name": name, "customer_email": email,
             "total": str(order.total), "currency": order.currency, "status": order.status,
             "payment_status": order.payment_status,
             "created_at": order.created_at.isoformat() if order.created_at else None}
            for order, name, email in recent_rows
        ],
    }


@router.get("/products")
async def admin_products(
    q: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db), _: User = Depends(require_admin),
):
    statement = select(Product)
    if q and q.strip():
        term = f"%{q.strip()}%"
        statement = statement.where(or_(Product.name.ilike(term), Product.sku.ilike(term), Product.category.ilike(term)))
    total = await db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    rows = (await db.scalars(statement.order_by(Product.created_at.desc()).offset((page - 1) * page_size).limit(page_size))).all()
    return {"items": [serialize_product(row) for row in rows], "total": int(total), "page": page, "page_size": page_size}


@router.post("/products", status_code=201)
async def create_product(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
    _: User = Depends(require_admin),
):
    existing = await db.scalar(select(Product.id).where(or_(Product.sku == payload.sku, Product.slug == payload.slug)))
    if existing:
        raise HTTPException(status_code=409, detail="SKU or slug already exists")
    product = Product(**payload.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    await invalidate_catalog_cache(redis)
    return serialize_product(product)


@router.patch("/products/{product_id}")
async def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
    _: User = Depends(require_admin),
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    changes = payload.model_dump(exclude_unset=True)
    candidate_sku = changes.get("sku", product.sku)
    candidate_slug = changes.get("slug", product.slug)
    duplicate = await db.scalar(
        select(Product.id).where(
            Product.id != product.id,
            or_(Product.sku == candidate_sku, Product.slug == candidate_slug),
        )
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="SKU or slug already exists")
    for key, value in changes.items():
        setattr(product, key, value)
    await db.commit()
    await db.refresh(product)
    await invalidate_catalog_cache(redis)
    return serialize_product(product)


@router.delete("/products/{product_id}", status_code=204)
async def archive_product(
    product_id: UUID,
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
    _: User = Depends(require_admin),
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    await db.commit()
    await invalidate_catalog_cache(redis)


@router.get("/offers")
async def admin_offers(db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    rows = (await db.scalars(select(Offer).order_by(Offer.sort_order, Offer.created_at.desc()))).all()
    return {"items": [serialize_offer(row) for row in rows]}


@router.post("/offers", status_code=201)
async def create_offer(payload: OfferCreate, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    offer = Offer(**payload.model_dump())
    db.add(offer)
    await db.commit()
    await db.refresh(offer)
    return serialize_offer(offer)


@router.patch("/offers/{offer_id}")
async def update_offer(offer_id: UUID, payload: OfferUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    offer = await db.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    changes = payload.model_dump(exclude_unset=True)
    effective_start = changes.get("starts_at", offer.starts_at)
    effective_end = changes.get("ends_at", offer.ends_at)
    if effective_start and effective_end and effective_end <= effective_start:
        raise HTTPException(status_code=422, detail="Offer end time must be later than its start time")
    for key, value in changes.items():
        setattr(offer, key, value)
    await db.commit()
    await db.refresh(offer)
    return serialize_offer(offer)


@router.delete("/offers/{offer_id}", status_code=204)
async def delete_offer(offer_id: UUID, db: AsyncSession = Depends(get_db), _: User = Depends(require_admin)):
    offer = await db.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    await db.delete(offer)
    await db.commit()


@router.get("/customers")
async def admin_customers(
    q: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db), _: User = Depends(require_admin),
):
    statement = select(User).where(User.role == "customer")
    if q and q.strip():
        term = f"%{q.strip()}%"
        statement = statement.where(or_(User.name.ilike(term), User.email.ilike(term), User.phone.ilike(term)))
    total = await db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    rows = (await db.scalars(statement.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size))).all()
    return {"items": [
        {"id": str(row.id), "name": row.name, "email": row.email, "phone": row.phone,
         "whatsapp_opt_in": row.whatsapp_opt_in, "is_active": row.is_active,
         "created_at": row.created_at.isoformat() if row.created_at else None}
        for row in rows
    ], "total": int(total), "page": page, "page_size": page_size}


@router.get("/orders")
async def admin_orders(
    q: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db), _: User = Depends(require_admin),
):
    statement = select(Order, User.name, User.email).join(User, User.id == Order.user_id)
    if q and q.strip():
        term = f"%{q.strip()}%"
        statement = statement.where(or_(Order.order_number.ilike(term), User.name.ilike(term), User.email.ilike(term)))
    total = await db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    rows = (await db.execute(statement.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size))).all()
    return {"items": [
        {"id": str(order.id), "order_number": order.order_number, "customer_name": name,
         "customer_email": email, "status": order.status, "payment_status": order.payment_status,
         "subtotal": str(order.subtotal), "shipping_fee": str(order.shipping_fee), "total": str(order.total),
         "currency": order.currency, "payment_provider": order.payment_provider,
         "payment_reference": order.payment_reference,
         "created_at": order.created_at.isoformat() if order.created_at else None}
        for order, name, email in rows
    ], "total": int(total), "page": page, "page_size": page_size}


@router.get("/payments")
async def admin_payments(
    q: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100),
    db: AsyncSession = Depends(get_db), _: User = Depends(require_admin),
):
    statement = select(Order, User.name, User.email, PaymentTransaction).join(User, User.id == Order.user_id).outerjoin(
        PaymentTransaction, PaymentTransaction.order_id == Order.id
    )
    if q and q.strip():
        term = f"%{q.strip()}%"
        statement = statement.where(or_(
            Order.order_number.ilike(term), Order.payment_reference.ilike(term),
            User.name.ilike(term), User.email.ilike(term), PaymentTransaction.provider.ilike(term),
            PaymentTransaction.reference.ilike(term), PaymentTransaction.provider_transaction_id.ilike(term),
        ))
    total = await db.scalar(select(func.count()).select_from(statement.subquery())) or 0
    rows = (await db.execute(statement.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size))).all()
    return {"items": [
        {"order_number": order.order_number, "customer_name": name, "customer_email": email,
         "provider": payment.provider if payment else order.payment_provider,
         "status": payment.status if payment else order.payment_status,
         "reference": (payment.provider_transaction_id or payment.reference) if payment else order.payment_reference,
         "amount": str(payment.amount if payment else order.total),
         "currency": payment.currency if payment else order.currency,
         "created_at": (payment.created_at if payment else order.created_at).isoformat() if (payment and payment.created_at) or order.created_at else None}
        for order, name, email, payment in rows
    ], "total": int(total), "page": page, "page_size": page_size}
