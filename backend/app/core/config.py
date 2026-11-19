from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    app_name: str = "NOVA HOME API"
    debug: bool = False
    secret_key: SecretStr = SecretStr("unsafe-development-secret-change-me")
    access_token_minutes: int = 15
    refresh_token_days: int = 14
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    cors_origins: str = "http://localhost:3000"
    database_url: str = "postgresql+asyncpg://nova:nova_dev_password@localhost:5432/nova_home"
    redis_url: str = "redis://localhost:6379/0"
    frontend_url: str = "http://localhost:3000"
    api_public_url: str = "http://localhost:8000"
    admin_bootstrap_email: str = ""
    media_dir: str = "/app/media"

    kashier_env: Literal["test", "live"] = "test"
    kashier_api_key: str = ""
    kashier_secret_key: SecretStr = SecretStr("")
    kashier_merchant_id: str = ""
    kashier_payment_type: str = "credit"

    whatsapp_enabled: bool = False
    whatsapp_graph_version: str = "v23.0"
    whatsapp_access_token: SecretStr = SecretStr("")
    whatsapp_phone_number_id: str = ""
    whatsapp_welcome_template: str = "welcome_customer"
    whatsapp_receipt_template: str = "order_receipt"
    whatsapp_template_language: str = "en"

    google_client_id: str = ""
    google_client_secret: SecretStr = SecretStr("")
    facebook_client_id: str = ""
    facebook_client_secret: SecretStr = SecretStr("")
    facebook_graph_version: str = "v26.0"
    apple_client_id: str = ""
    apple_client_secret: SecretStr = SecretStr("")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def kashier_base_url(self) -> str:
        return "https://test-api.kashier.io" if self.kashier_env == "test" else "https://api.kashier.io"

    def validate_runtime_settings(self) -> None:
        if self.app_env == "production":
            secret = self.secret_key.get_secret_value()
            if len(secret) < 48 or secret.lower().startswith(("change", "unsafe", "generate")):
                raise RuntimeError("Production SECRET_KEY must be a unique random value of at least 48 chars")
            if not self.cookie_secure:
                raise RuntimeError("COOKIE_SECURE must be true in production")
            if self.debug:
                raise RuntimeError("DEBUG must be false in production")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_runtime_settings()
    return settings
