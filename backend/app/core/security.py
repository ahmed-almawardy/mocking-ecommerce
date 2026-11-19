from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerificationError, VerifyMismatchError

from app.core.config import get_settings

password_hash = PasswordHasher()
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return password_hash.verify(hashed, password)
    except (InvalidHash, VerificationError, VerifyMismatchError):
        return False


def create_token(subject: str, token_type: str, expires_delta: timedelta) -> tuple[str, str, int]:
    settings = get_settings()
    now = datetime.now(UTC)
    expires = now + expires_delta
    jti = str(uuid4())
    payload = {
        "sub": subject,
        "type": token_type,
        "jti": jti,
        "iat": now,
        "exp": expires,
    }
    encoded = jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm=ALGORITHM)
    return encoded, jti, int(expires.timestamp())


def create_token_pair(subject: str) -> dict[str, tuple[str, str, int]]:
    settings = get_settings()
    return {
        "access": create_token(subject, "access", timedelta(minutes=settings.access_token_minutes)),
        "refresh": create_token(subject, "refresh", timedelta(days=settings.refresh_token_days)),
    }


def decode_token(token: str) -> dict:
    settings = get_settings()
    return jwt.decode(token, settings.secret_key.get_secret_value(), algorithms=[ALGORITHM])


def token_max_age_seconds(token_type: str) -> int:
    settings = get_settings()
    return settings.access_token_minutes * 60 if token_type == "access" else settings.refresh_token_days * 86400
