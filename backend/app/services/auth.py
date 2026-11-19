import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models import AuthIdentity, User


def normalize_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("00"):
        digits = digits[2:]
    if len(digits) == 11 and digits.startswith("01"):
        digits = "20" + digits[1:]
    elif len(digits) == 10 and digits.startswith(("10", "11", "12", "15")):
        digits = "20" + digits
    if not 8 <= len(digits) <= 15:
        raise ValueError("Enter a valid phone number with its country code")
    return f"+{digits}"


async def register_user(db: AsyncSession, *, name: str, email: str, phone: str, password: str, whatsapp_opt_in: bool) -> User:
    normalized_email = email.strip().lower()
    normalized_phone = normalize_phone(phone)
    existing = await db.scalar(select(User).where((User.email == normalized_email) | (User.phone == normalized_phone)))
    if existing:
        raise ValueError("An account with this email address or phone number already exists")
    user = User(
        name=name.strip(),
        email=normalized_email,
        phone=normalized_phone,
        password_hash=hash_password(password),
        whatsapp_opt_in=whatsapp_opt_in,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    user = await db.scalar(select(User).where(User.email == email.strip().lower()))
    if not user or not user.is_active or not user.password_hash:
        return None
    return user if verify_password(password, user.password_hash) else None


async def resolve_oauth_identity(
    db: AsyncSession,
    *, provider: str,
    subject: str,
    email: str | None,
    name: str | None,
    email_verified: bool,
) -> User:
    identity = await db.scalar(select(AuthIdentity).where(
        AuthIdentity.provider == provider, AuthIdentity.subject == subject
    ))
    if identity:
        return await db.get(User, identity.user_id)

    normalized_email = email.strip().lower() if email else None
    existing_user = None
    if normalized_email:
        existing_user = await db.scalar(select(User).where(User.email == normalized_email))

    if existing_user:
        # Never silently merge identities based on an unverified provider email.
        if not email_verified:
            raise ValueError("This email already has an account. Sign in first, then link this provider from account settings.")
        user = existing_user
        if email_verified:
            user.email_verified = True
    else:
        if not normalized_email:
            raise ValueError("The provider did not return an email address. Use email registration instead.")
        user = User(
            name=(name or normalized_email.split("@")[0])[:160],
            email=normalized_email,
            email_verified=email_verified,
        )
        db.add(user)
        await db.flush()

    db.add(AuthIdentity(user_id=user.id, provider=provider, subject=subject, provider_email=normalized_email))
    await db.commit()
    await db.refresh(user)
    return user
