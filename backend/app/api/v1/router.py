from fastapi import APIRouter

from app.api.v1 import admin, analytics, auth, offers, orders, products, webhooks

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(analytics.router)
api_router.include_router(products.router)
api_router.include_router(offers.router)
api_router.include_router(orders.router)
api_router.include_router(webhooks.router)
