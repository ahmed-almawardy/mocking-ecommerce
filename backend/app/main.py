from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import from_url
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.db.session import engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    await app.state.redis.ping()
    yield
    await app.state.redis.aclose()
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="NOVA HOME commerce API — catalog, customer identity, checkout, Kashier and WhatsApp integrations.",
    docs_url="/docs" if settings.app_env != "production" else None,
    redoc_url=None,
    lifespan=lifespan,
)
# Authlib uses a signed, short-lived session cookie to validate OAuth state.
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key.get_secret_value(),
    same_site="none" if settings.cookie_secure else "lax",
    https_only=settings.cookie_secure,
    max_age=600,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Kashier-Signature"],
)
app.include_router(api_router)
Path(settings.media_dir).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")


@app.middleware("http")
async def enforce_browser_origin(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        path = request.url.path
        is_provider_callback = path.startswith("/api/v1/auth/") and path.endswith("/callback")
        is_webhook = path.startswith("/api/v1/webhooks/")
        origin = request.headers.get("origin")
        if origin and not is_provider_callback and not is_webhook and origin not in settings.cors_origin_list:
            return JSONResponse(status_code=403, content={"detail": "Request origin is not allowed"})
    return await call_next(request)


@app.get("/health", tags=["operations"])
async def health():
    return {"status": "ok", "environment": settings.app_env}
