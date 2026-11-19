from datetime import UTC, datetime
import json
import logging
import hashlib
import secrets
from urllib.parse import parse_qs, urlparse
from uuid import UUID

import jwt
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_redis
from app.core.config import get_settings
from app.core.oauth import oauth
from app.core.oauth_config import (
    SUPPORTED_OAUTH_PROVIDERS,
    oauth_callback_url,
    oauth_provider_status,
)
from app.core.security import create_token_pair, decode_token, token_max_age_seconds
from app.db.session import get_db
from app.models import AuthIdentity, User
from app.schemas.auth import (
    AuthMessage, LoginRequest, RegisterRequest, UserOut,
    MobileLoginRequest, MobileRefreshRequest, MobileLogoutRequest,
    MobileExchangeRequest, MobileTokenResponse,
)
from app.services.auth import authenticate_user, register_user, resolve_oauth_identity
from app.services.notifications.whatsapp import send_welcome

router = APIRouter(prefix="/auth", tags=["authentication"])
logger = logging.getLogger(__name__)


def mobile_token_response(user: User, pair: dict) -> MobileTokenResponse:
    access, _, _ = pair["access"]
    refresh, _, _ = pair["refresh"]
    return MobileTokenResponse(
        access_token=access, refresh_token=refresh,
        expires_in=token_max_age_seconds("access"),
        refresh_expires_in=token_max_age_seconds("refresh"),
        user=UserOut.model_validate(user),
    )


@router.post("/mobile/login", response_model=MobileTokenResponse)
async def mobile_login(payload: MobileLoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, str(payload.email), payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    return mobile_token_response(user, create_token_pair(str(user.id)))


@router.post("/mobile/register", response_model=MobileTokenResponse, status_code=201)
async def mobile_register(payload: RegisterRequest, background: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    try:
        user = await register_user(
            db, name=payload.name, email=str(payload.email), phone=payload.phone,
            password=payload.password, whatsapp_opt_in=payload.whatsapp_opt_in,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if user.whatsapp_opt_in and user.phone:
        background.add_task(send_welcome, user.phone, user.name)
    return mobile_token_response(user, create_token_pair(str(user.id)))


@router.post("/mobile/refresh", response_model=MobileTokenResponse)
async def mobile_refresh(payload: MobileRefreshRequest, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    try:
        claims = decode_token(payload.refresh_token)
        if claims.get("type") != "refresh" or await redis.exists(f"jwt:blacklist:{claims['jti']}"):
            raise ValueError("Invalid refresh token")
        user = await db.get(User, UUID(claims["sub"]))
        if not user or not user.is_active:
            raise ValueError("Account is unavailable")
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Refresh session is invalid") from None
    await revoke_token(redis, payload.refresh_token)
    return mobile_token_response(user, create_token_pair(str(user.id)))


@router.post("/mobile/logout")
async def mobile_logout(payload: MobileLogoutRequest, redis: Redis = Depends(get_redis)):
    await revoke_token(redis, payload.access_token)
    await revoke_token(redis, payload.refresh_token)
    return {"message": "Signed out"}


@router.post("/mobile/exchange", response_model=MobileTokenResponse)
async def mobile_exchange(payload: MobileExchangeRequest, redis: Redis = Depends(get_redis)):
    code_hash = hashlib.sha256(payload.code.encode()).hexdigest()
    stored = await redis.getdel(f"oauth:exchange:{code_hash}")
    if not stored:
        raise HTTPException(status_code=401, detail="Mobile sign-in code is invalid or expired")
    try:
        data = json.loads(stored)
        return MobileTokenResponse.model_validate(data)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Mobile sign-in code is invalid") from None


@router.get("/{provider}/mobile-login", name="oauth_mobile_login")
async def oauth_mobile_login(
    provider: str, request: Request, redirect_uri: str, app_type: str = "customer",
    redis: Redis = Depends(get_redis),
):
    if provider not in SUPPORTED_OAUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unsupported sign-in provider")
    if app_type not in {"customer", "admin"}:
        raise HTTPException(status_code=422, detail="Unsupported mobile app type")
    parsed = urlparse(redirect_uri)
    allowed_schemes = {"novahome", "novahomeadmin"}
    if parsed.scheme not in allowed_schemes or parsed.netloc != "auth":
        raise HTTPException(status_code=400, detail="Mobile redirect URI is not allowed")
    expected_scheme = "novahome" if app_type == "customer" else "novahomeadmin"
    if parsed.scheme != expected_scheme:
        raise HTTPException(status_code=400, detail="Mobile redirect URI does not match app type")
    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(status_code=503, detail=f"{provider.title()} sign-in is not configured")
    settings = get_settings()
    if provider == "apple" and not settings.cookie_secure:
        raise HTTPException(status_code=503, detail="Apple sign-in requires HTTPS and COOKIE_SECURE=true")
    response = await client.authorize_redirect(request, oauth_callback_url(provider))
    location = response.headers.get("location", "")
    state = parse_qs(urlparse(location).query).get("state", [None])[0]
    if not state:
        raise HTTPException(status_code=502, detail="Could not initialise mobile sign-in")
    await redis.setex(f"oauth:mobile:{state}", 600, json.dumps({"redirect_uri": redirect_uri, "app_type": app_type}))
    return response
def set_auth_cookies(response: Response, pair: dict) -> None:
    settings = get_settings()
    access, _, _ = pair["access"]
    refresh, _, _ = pair["refresh"]
    common = {"httponly": True, "secure": settings.cookie_secure, "samesite": settings.cookie_samesite, "path": "/"}
    response.set_cookie("access_token", access, max_age=settings.access_token_minutes * 60, **common)
    response.set_cookie("refresh_token", refresh, max_age=settings.refresh_token_days * 86400, **common)


async def revoke_token(redis: Redis, token: str | None) -> None:
    if not token:
        return
    try:
        payload = decode_token(token)
        exp = int(payload["exp"])
        ttl = max(1, exp - int(datetime.now(UTC).timestamp()))
        await redis.setex(f"jwt:blacklist:{payload['jti']}", ttl, "1")
    except (jwt.PyJWTError, KeyError, ValueError):
        return


@router.post("/register", response_model=AuthMessage, status_code=201)
async def register(payload: RegisterRequest, response: Response, background: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    try:
        user = await register_user(
            db, name=payload.name, email=str(payload.email), phone=payload.phone,
            password=payload.password, whatsapp_opt_in=payload.whatsapp_opt_in,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    set_auth_cookies(response, create_token_pair(str(user.id)))
    if user.whatsapp_opt_in and user.phone:
        background.add_task(send_welcome, user.phone, user.name)
    return AuthMessage(message="Your NOVA HOME account has been created", user=UserOut.model_validate(user))


@router.post("/login", response_model=AuthMessage)
async def login(payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, str(payload.email), payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email or password is incorrect")
    set_auth_cookies(response, create_token_pair(str(user.id)))
    return AuthMessage(message="Welcome back", user=UserOut.model_validate(user))


@router.post("/refresh", response_model=AuthMessage)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Refresh session is missing")
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh" or await redis.exists(f"jwt:blacklist:{payload['jti']}"):
            raise ValueError("Invalid refresh token")
        user = await db.get(User, UUID(payload["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Refresh session is invalid") from None
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Account is unavailable")
    await revoke_token(redis, token)
    pair = create_token_pair(str(user.id))
    set_auth_cookies(response, pair)
    return AuthMessage(message="Session refreshed", user=UserOut.model_validate(user))


@router.post("/logout")
async def logout(request: Request, response: Response, redis: Redis = Depends(get_redis)):
    await revoke_token(redis, request.cookies.get("access_token"))
    await revoke_token(redis, request.cookies.get("refresh_token"))
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return {"message": "Signed out"}


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


@router.get("/providers")
async def oauth_providers():
    """Public, secret-free provider status and exact callback URLs for setup diagnostics."""
    return {"providers": oauth_provider_status()}


@router.get("/{provider}/login", name="oauth_login")
async def oauth_login(provider: str, request: Request):
    if provider not in SUPPORTED_OAUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unsupported sign-in provider")
    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(status_code=503, detail=f"{provider.title()} sign-in is not configured. Add its OAuth client ID and secret to the API environment, then rebuild/restart the API.")
    settings = get_settings()
    if provider == "apple" and not settings.cookie_secure:
        raise HTTPException(status_code=503, detail="Apple web sign-in requires HTTPS with COOKIE_SECURE=true because Apple returns to the server using a cross-site form POST.")
    redirect_uri = oauth_callback_url(provider)
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/{provider}/link", name="oauth_link")
async def oauth_link(
    provider: str,
    request: Request,
    user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    if provider not in SUPPORTED_OAUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unsupported sign-in provider")
    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(status_code=503, detail=f"{provider.title()} sign-in is not configured. Add its OAuth client ID and secret to the API environment, then rebuild/restart the API.")
    settings = get_settings()
    if provider == "apple" and not settings.cookie_secure:
        raise HTTPException(status_code=503, detail="Apple web sign-in requires HTTPS with COOKIE_SECURE=true because Apple returns to the server using a cross-site form POST.")
    redirect_uri = oauth_callback_url(provider)
    response = await client.authorize_redirect(request, redirect_uri)
    location = response.headers.get("location", "")
    state = parse_qs(urlparse(location).query).get("state", [None])[0]
    if not state:
        raise HTTPException(status_code=502, detail="Could not initialise provider account linking")
    await redis.setex(f"oauth:link:{state}", 600, str(user.id))
    return response


@router.api_route("/{provider}/callback", methods=["GET", "POST"], name="oauth_callback")
async def oauth_callback(provider: str, request: Request, db: AsyncSession = Depends(get_db), redis: Redis = Depends(get_redis)):
    if provider not in SUPPORTED_OAUTH_PROVIDERS:
        raise HTTPException(status_code=404, detail="Unsupported sign-in provider")
    client = oauth.create_client(provider)
    if client is None:
        raise HTTPException(status_code=503, detail=f"{provider.title()} sign-in is not configured")
    state = request.query_params.get("state")
    callback_form = None
    if not state and request.method == "POST":
        # Apple may return OAuth state in an application/x-www-form-urlencoded
        # form body when response_mode=form_post is used.
        callback_form = await request.form()
        state = str(callback_form.get("state") or "") or None
    try:
        token = await client.authorize_access_token(request)
        if provider == "facebook":
            result = await client.get("me", token=token, params={"fields": "id,name,email"})
            result.raise_for_status()
            profile = result.json()
            subject = str(profile["id"])
            email = profile.get("email")
            name = profile.get("name")
            # Facebook Login's /me response does not provide Google's/Apple's
            # email_verified OIDC claim. Never auto-merge an existing account
            # based only on a matching Facebook email; require explicit linking.
            email_verified = False
        else:
            profile = token.get("userinfo")
            if not profile and token.get("id_token"):
                profile = await client.parse_id_token(request, token)
            if not profile:
                raise ValueError("Provider did not return an identity profile")
            subject = str(profile.get("sub") or profile.get("id"))
            email = profile.get("email")
            name = profile.get("name")
            email_verified = profile.get("email_verified") is True or profile.get("email_verified") == "true"
            if provider == "apple" and request.method == "POST":
                # Apple supplies the customer's name in a separate `user` form
                # field on the first authorization only; it is not an ID-token claim.
                form_data = callback_form or await request.form()
                apple_user_json = form_data.get("user")
                if apple_user_json:
                    apple_user = json.loads(str(apple_user_json))
                    apple_name = apple_user.get("name") or {}
                    first_name = str(apple_name.get("firstName") or "").strip()
                    last_name = str(apple_name.get("lastName") or "").strip()
                    name = " ".join(part for part in (first_name, last_name) if part) or name
        if not state and request.method == "POST":
            form_data = callback_form or await request.form()
            state = str(form_data.get("state") or "") or None
        link_user_id = await redis.get(f"oauth:link:{state}") if state else None
        if link_user_id:
            existing_identity = await db.scalar(
                select(AuthIdentity).where(
                    AuthIdentity.provider == provider, AuthIdentity.subject == subject
                )
            )
            if existing_identity and str(existing_identity.user_id) != link_user_id:
                raise ValueError("This provider account is already connected to another NOVA HOME account.")
            if not existing_identity:
                db.add(AuthIdentity(user_id=UUID(link_user_id), provider=provider, subject=subject, provider_email=email))
                await db.commit()
            user = await db.get(User, UUID(link_user_id))
            await redis.delete(f"oauth:link:{state}")
            if not user or not user.is_active:
                raise ValueError("The account selected for linking is not available.")
        else:
            user = await resolve_oauth_identity(
                db, provider=provider, subject=subject, email=email, name=name, email_verified=email_verified,
            )
    except ValueError as exc:
        message = str(exc)
        logger.warning("OAuth identity resolution rejected provider %s: %s", provider, message)
        if "already has an account" in message or "already connected to another" in message:
            error_code = "account_link_required"
        elif "did not return an email address" in message:
            error_code = "provider_email_missing"
        else:
            error_code = "provider_callback_failed"
        mobile_error = await redis.get(f"oauth:mobile:{state}") if state else None
        if mobile_error:
            mobile = json.loads(mobile_error)
            await redis.delete(f"oauth:mobile:{state}")
            return RedirectResponse(url=f"{mobile['redirect_uri']}?error={error_code}", status_code=303)
        return RedirectResponse(
            url=f"{get_settings().frontend_url.rstrip('/')}/auth/login?oauth_error={error_code}",
            status_code=303,
        )
    except Exception:
        logger.exception("OAuth callback failed for provider %s", provider)
        mobile_error = await redis.get(f"oauth:mobile:{state}") if state else None
        if mobile_error:
            mobile = json.loads(mobile_error)
            await redis.delete(f"oauth:mobile:{state}")
            return RedirectResponse(url=f"{mobile['redirect_uri']}?error=provider_callback_failed", status_code=303)
        return RedirectResponse(
            url=f"{get_settings().frontend_url.rstrip('/')}/auth/login?oauth_error=provider_callback_failed",
            status_code=303,
        )

    mobile_state = await redis.get(f"oauth:mobile:{state}") if state else None
    if mobile_state:
        mobile = json.loads(mobile_state)
        expected_role = mobile.get("app_type")
        if expected_role == "admin" and user.role not in {"admin", "super_admin"}:
            await redis.delete(f"oauth:mobile:{state}")
            return RedirectResponse(url=f"{mobile['redirect_uri']}?error=admin_role_required", status_code=303)
        if expected_role == "customer" and user.role != "customer":
            await redis.delete(f"oauth:mobile:{state}")
            return RedirectResponse(url=f"{mobile['redirect_uri']}?error=customer_account_required", status_code=303)
        pair = create_token_pair(str(user.id))
        code = secrets.token_urlsafe(32)
        access, _, _ = pair["access"]
        refresh, _, _ = pair["refresh"]
        exchange_data = mobile_token_response(user, pair).model_dump(mode="json")
        code_hash = hashlib.sha256(code.encode()).hexdigest()
        await redis.setex(f"oauth:exchange:{code_hash}", 90, json.dumps(exchange_data))
        await redis.delete(f"oauth:mobile:{state}")
        return RedirectResponse(url=f"{mobile['redirect_uri']}?code={code}", status_code=303)

    response = RedirectResponse(url=f"{get_settings().frontend_url.rstrip('/')}/account", status_code=303)
    set_auth_cookies(response, create_token_pair(str(user.id)))
    return response
