from collections.abc import AsyncGenerator
from typing import Any
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db
from app.models import User


async def get_redis(request: Request) -> AsyncGenerator[Any, None]:
    yield request.app.state.redis


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
    redis: Any = Depends(get_redis),
) -> User:
    token = request.cookies.get("access_token")
    authorization = request.headers.get("Authorization", "")
    if not token and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise ValueError("Wrong token type")
        if await redis.exists(f"jwt:blacklist:{payload['jti']}"):
            raise ValueError("Token has been revoked")
        user = await db.get(User, UUID(payload["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session") from None
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is unavailable")
    return user
