import re
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    phone: str = Field(min_length=8, max_length=32)
    password: str = Field(min_length=10, max_length=128)
    whatsapp_opt_in: bool = False

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value)
        if not 8 <= len(digits) <= 15:
            raise ValueError("Enter a valid phone number with its country code")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    email: str | None
    phone: str | None
    whatsapp_opt_in: bool
    email_verified: bool
    role: str = "customer"


class AuthMessage(BaseModel):
    message: str
    user: UserOut | None = None


class MobileLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class MobileRefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=20, max_length=4096)


class MobileLogoutRequest(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None


class MobileExchangeRequest(BaseModel):
    code: str = Field(min_length=20, max_length=256)


class MobileTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_expires_in: int
    user: UserOut
