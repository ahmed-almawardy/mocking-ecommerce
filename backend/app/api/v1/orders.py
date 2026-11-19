import secrets
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pathlib import Path

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Order, OrderItem, PaymentTransaction, Product, User
from app.schemas.products import CreateOrderRequest
from app.services.payments.kashier import KashierError, create_payment_session

router = APIRouter(prefix="/orders", tags=["orders & checkout"])


@router.post("")
async def create_order(payload: CreateOrderRequest, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    quantities: dict = {}
    for line in payload.items:
        quantities[line.product_id] = quantities.get(line.product_id, 0) + line.quantity
        if quantities[line.product_id] > 20:
            raise HTTPException(status_code=422, detail="A product quantity cannot exceed 20 per order")
    product_ids = list(quantities)
    products = (await db.scalars(
        select(Product).where(Product.id.in_(product_ids), Product.is_active.is_(True))
        .order_by(Product.id).with_for_update()
    )).all()
    products_by_id = {product.id: product for product in products}
    if len(products_by_id) != len(product_ids):
        raise HTTPException(status_code=400, detail="One or more products are unavailable")

    subtotal = Decimal("0.00")
    item_rows = []
    for product_id, quantity in quantities.items():
        product = products_by_id[product_id]
        if product.stock_qty < quantity:
            raise HTTPException(status_code=409, detail=f"Not enough stock for {product.name}")
        line_total = product.price * quantity
        subtotal += line_total
        item_rows.append((product, quantity, line_total))

    shipping_fee = Decimal("0.00") if subtotal >= Decimal("2000.00") else Decimal("75.00")
    order_number = f"NH-{secrets.token_hex(6).upper()}"
    order = Order(
        order_number=order_number, user_id=user.id, status="pending_payment", payment_status="pending",
        subtotal=subtotal, shipping_fee=shipping_fee, total=subtotal + shipping_fee,
        shipping_name=payload.shipping_name, shipping_phone=payload.shipping_phone,
        shipping_address=payload.shipping_address, shipping_city=payload.shipping_city,
    )
    db.add(order)
    await db.flush()
    db.add(PaymentTransaction(order_id=order.id, provider=order.payment_provider, status="pending", amount=order.total, currency=order.currency))
    for product, quantity, line_total in item_rows:
        db.add(OrderItem(
            order_id=order.id, product_id=product.id, product_name=product.name, sku=product.sku,
            quantity=quantity, unit_price=product.price, line_total=line_total,
        ))
    await db.commit()
    try:
        payment_url = await create_payment_session(
            order_number=order.order_number,
            amount=order.total,
            customer_email=user.email or "",
            customer_id=str(user.id),
        )
    except KashierError as exc:
        order.status = "payment_setup_failed"
        await db.commit()
        raise HTTPException(
            status_code=503,
            detail=f"Order {order.order_number} was saved, but payment setup failed. Retry payment from this order or contact support. ({exc})",
        ) from exc
    return {
        "order_number": order.order_number,
        "status": order.status,
        "payment_status": order.payment_status,
        "subtotal": str(order.subtotal),
        "shipping_fee": str(order.shipping_fee),
        "total": str(order.total),
        "currency": order.currency,
        "payment_url": payment_url,
    }


@router.get("")
async def list_orders(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    orders = (await db.scalars(
        select(Order).options(selectinload(Order.items))
        .where(Order.user_id == user.id)
        .order_by(Order.created_at.desc()).limit(50)
    )).all()
    return [
        {
            "order_number": order.order_number,
            "status": order.status,
            "payment_status": order.payment_status,
            "subtotal": str(order.subtotal),
            "shipping_fee": str(order.shipping_fee),
            "total": str(order.total),
            "currency": order.currency,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "receipt_available": bool(order.receipt_path and Path(order.receipt_path).is_file()),
            "items": [
                {"product_name": item.product_name, "quantity": item.quantity, "line_total": str(item.line_total)}
                for item in order.items
            ],
        }
        for order in orders
    ]


@router.post("/{order_number}/payment-session")
async def retry_payment_session(
    order_number: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = await db.scalar(select(Order).where(Order.order_number == order_number, Order.user_id == user.id).with_for_update())
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.payment_status != "pending" or order.status not in {"payment_setup_failed", "pending_payment"}:
        raise HTTPException(status_code=409, detail="This order is not awaiting payment")
    try:
        payment_url = await create_payment_session(
            order_number=order.order_number,
            amount=order.total,
            customer_email=user.email or "",
            customer_id=str(user.id),
        )
    except KashierError as exc:
        raise HTTPException(status_code=503, detail=f"Payment is temporarily unavailable: {exc}") from exc
    order.status = "pending_payment"
    await db.commit()
    return {"order_number": order.order_number, "payment_url": payment_url}


@router.get("/{order_number}/receipt.pdf")
async def download_receipt(
    order_number: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = await db.scalar(
        select(Order).where(Order.order_number == order_number, Order.user_id == user.id)
    )
    if not order or not order.receipt_path or not Path(order.receipt_path).is_file():
        raise HTTPException(status_code=404, detail="Receipt is not available yet")
    return FileResponse(
        order.receipt_path, media_type="application/pdf",
        filename=f"NOVA-HOME-{order.order_number}-receipt.pdf",
    )


@router.get("/{order_number}")
async def get_order(order_number: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    order = await db.scalar(
        select(Order).options(selectinload(Order.items)).where(Order.order_number == order_number, Order.user_id == user.id)
    )
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "order_number": order.order_number, "status": order.status, "payment_status": order.payment_status,
        "subtotal": str(order.subtotal), "shipping_fee": str(order.shipping_fee), "total": str(order.total),
        "currency": order.currency,
        "items": [{"product_name": i.product_name, "sku": i.sku, "quantity": i.quantity, "unit_price": str(i.unit_price), "line_total": str(i.line_total)} for i in order.items],
    }
