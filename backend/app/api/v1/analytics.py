from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Product, ProductEvent

router = APIRouter(prefix="/analytics", tags=["store analytics"])


class ProductEventIn(BaseModel):
    product_id: UUID
    event_type: Literal["view", "add_to_cart"]
    quantity: int = Field(default=1, ge=1, le=20)
    session_key: str | None = Field(default=None, min_length=12, max_length=80)


@router.post("/events", status_code=202)
async def record_product_event(payload: ProductEventIn, db: AsyncSession = Depends(get_db)):
    product = await db.get(Product, payload.product_id)
    if not product or not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")
    db.add(ProductEvent(
        product_id=product.id,
        event_type=payload.event_type,
        quantity=payload.quantity if payload.event_type == "add_to_cart" else 1,
        session_key=payload.session_key,
    ))
    await db.commit()
    return {"accepted": True}
