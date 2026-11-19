"""Pure OAuth configuration helpers shared by API routes and diagnostics."""

from app.core.config import get_settings

SUPPORTED_OAUTH_PROVIDERS = ("google", "facebook", "apple")


def oauth_callback_url(provider: str) -> str:
    """Build a deterministic public callback URL, independent of proxy Host headers."""
    if provider not in SUPPORTED_OAUTH_PROVIDERS:
        raise ValueError("Unsupported OAuth provider")
    base = get_settings().api_public_url.rstrip("/")
    return f"{base}/api/v1/auth/{provider}/callback"


def provider_configuration() -> dict[str, bool]:
    settings = get_settings()
    return {
        "google": bool(settings.google_client_id and settings.google_client_secret.get_secret_value()),
        "facebook": bool(settings.facebook_client_id and settings.facebook_client_secret.get_secret_value()),
        "apple": bool(settings.apple_client_id and settings.apple_client_secret.get_secret_value()),
    }


def oauth_provider_status() -> dict[str, dict[str, str | bool | None]]:
    """Return safe configuration diagnostics without exposing client credentials."""
    settings = get_settings()
    configured = provider_configuration()
    available = dict(configured)
    # Apple uses a cross-site form POST. It needs a Secure SameSite=None session cookie.
    if available["apple"] and not settings.cookie_secure:
        available["apple"] = False

    result: dict[str, dict[str, str | bool | None]] = {}
    for provider in SUPPORTED_OAUTH_PROVIDERS:
        reason = None
        if provider == "apple" and configured[provider] and not settings.cookie_secure:
            reason = "Apple web sign-in requires HTTPS and COOKIE_SECURE=true."
        elif not available[provider]:
            reason = "Provider credentials are not configured on the server."
        result[provider] = {
            "configured": configured[provider],
            "available": available[provider],
            "reason": reason,
            "callback_url": oauth_callback_url(provider),
        }
    return result
