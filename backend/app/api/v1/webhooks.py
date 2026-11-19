from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.db.session import AsyncSessionLocal
from app.models import Order, PaymentTransaction, Product
from app.services.notifications.whatsapp import upload_pdf_and_send_receipt
from app.services.payments.kashier import verify_webhook_signature
from app.services.receipts import generate_receipt

router = APIRouter(prefix="/webhooks", tags=["provider webhooks"])


async def process_paid_order(order_number: str) -> None:
    async with AsyncSessionLocal() as db:
        order = await db.scalar(
            select(Order).options(selectinload(Order.items), selectinload(Order.user))
            .where(Order.order_number == order_number).with_for_update()
        )
        if not order or order.payment_status != "paid":
            return
        if not order.receipt_path:
            order.receipt_path = generate_receipt(order)
        settings = get_settings()
        if (settings.whatsapp_enabled and order.user.whatsapp_opt_in and order.user.phone
                and not order.whatsapp_receipt_sent_at):
            await upload_pdf_and_send_receipt(
                order.user.phone, order.receipt_path, order.order_number, f"EGP {order.total:.2f}"
            )
            order.whatsapp_receipt_sent_at = datetime.now(UTC)
        await db.commit()


@router.post("/kashier")
async def kashier_webhook(request: Request, background: BackgroundTasks, x_kashier_signature: str | None = Header(default=None)):
    payload = await request.json()
    data = payload.get("data") or {}
    settings = get_settings()
    if not verify_webhook_signature(data, x_kashier_signature or "", settings.kashier_api_key):
        raise HTTPException(status_code=401, detail="Invalid Kashier webhook signature")

    # Kashier's event name does not determine success; data.status does.
    order_number = data.get("merchantOrderId") or data.get("orderReference") or data.get("order")
    if not order_number:
        raise HTTPException(status_code=400, detail="Webhook is missing the merchant order reference")

    async with AsyncSessionLocal() as db:
        order = await db.scalar(select(Order).options(selectinload(Order.items)).where(Order.order_number == str(order_number)).with_for_update())
        if not order:
            return Response(status_code=200)
        status_value = str(data.get("status", "")).upper()
        if status_value == "SUCCESS":
            try:
                received_amount = Decimal(str(data.get("amount")))
            except (InvalidOperation, TypeError, ValueError):
                raise HTTPException(status_code=400, detail="Successful payment webhook is missing a valid amount") from None
            received_currency = str(data.get("currency", "")).upper()
            if received_amount != order.total or received_currency != order.currency.upper():
                raise HTTPException(status_code=400, detail="Payment amount or currency does not match the order")
        transaction_id = data.get("transactionId") or data.get("kashierOrderId")
        payment = await db.scalar(select(PaymentTransaction).where(PaymentTransaction.order_id == order.id).with_for_update())
        if payment is None:
            payment = PaymentTransaction(
                order_id=order.id, provider=order.payment_provider, amount=order.total, currency=order.currency
            )
            db.add(payment)
        payment.last_event_at = datetime.now(UTC)
        if transaction_id:
            payment.provider_transaction_id = str(transaction_id)
        if data.get("paymentMethod"):
            payment.method = str(data.get("paymentMethod"))[:80]
        if status_value == "SUCCESS":
            payment.status = "paid"
        elif status_value == "FAILURE":
            payment.status = "failed"

        if status_value == "SUCCESS" and order.payment_status != "paid":
            # Lock product rows and commit inventory only after the payment is provider-confirmed.
            stock_ok = True
            for item in order.items:
                product = await db.scalar(select(Product).where(Product.id == item.product_id).with_for_update())
                if not product or product.stock_qty < item.quantity:
                    stock_ok = False
                    break
            if stock_ok:
                for item in order.items:
                    product = await db.get(Product, item.product_id)
                    product.stock_qty -= item.quantity
                order.payment_status = "paid"
                order.status = "processing"
                order.payment_reference = str(transaction_id) if transaction_id else None
                payment.status = "paid"
            else:
                order.payment_status = "paid"
                order.status = "manual_review"
                order.payment_reference = str(transaction_id) if transaction_id else None
                payment.status = "paid"
        elif status_value == "FAILURE" and order.payment_status == "pending":
            order.payment_status = "failed"
            order.status = "payment_failed"
            payment.status = "failed"
        await db.commit()
        if status_value == "SUCCESS":
            background.add_task(process_paid_order, str(order_number))
    return Response(status_code=200)
