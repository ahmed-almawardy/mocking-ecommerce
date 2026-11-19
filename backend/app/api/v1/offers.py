from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import Offer

router = APIRouter(prefix="/offers", tags=["store offers"])


@router.get("/active")
async def active_offers(db: AsyncSession = Depends(get_db)):
    now = datetime.now(UTC)
    rows = (await db.scalars(
        select(Offer)
        .where(
            Offer.is_active.is_(True),
            or_(Offer.starts_at.is_(None), Offer.starts_at <= now),
            or_(Offer.ends_at.is_(None), Offer.ends_at > now),
        )
        .order_by(Offer.sort_order.asc(), Offer.created_at.desc())
        .limit(4)
    )).all()
    return {"items": [
        {"id": str(row.id), "title": row.title, "subtitle": row.subtitle,
         "title_ar": row.title_ar, "subtitle_ar": row.subtitle_ar,
         "image_url": row.image_url, "link_url": row.link_url, "badge": row.badge}
        for row in rows
    ]}
