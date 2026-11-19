from app.core.config import get_settings
from app.core.oauth_config import oauth_callback_url, oauth_provider_status, provider_configuration


def test_callback_url_uses_configured_public_api_origin(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "api_public_url", "https://shop.example.test")
    assert oauth_callback_url("google") == "https://shop.example.test/api/v1/auth/google/callback"


def test_provider_configuration_is_false_without_credentials(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "google_client_id", "")
    monkeypatch.setattr(settings, "google_client_secret", type(settings.google_client_secret)(""))
    monkeypatch.setattr(settings, "facebook_client_id", "")
    monkeypatch.setattr(settings, "facebook_client_secret", type(settings.facebook_client_secret)(""))
    monkeypatch.setattr(settings, "apple_client_id", "")
    monkeypatch.setattr(settings, "apple_client_secret", type(settings.apple_client_secret)(""))
    assert provider_configuration() == {"google": False, "facebook": False, "apple": False}
    status = oauth_provider_status()
    assert all(item["available"] is False for item in status.values())


def test_apple_requires_secure_cookie_for_form_post(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "google_client_id", "google-id")
    monkeypatch.setattr(settings, "google_client_secret", type(settings.google_client_secret)("google-secret"))
    monkeypatch.setattr(settings, "facebook_client_id", "facebook-id")
    monkeypatch.setattr(settings, "facebook_client_secret", type(settings.facebook_client_secret)("facebook-secret"))
    monkeypatch.setattr(settings, "apple_client_id", "apple-id")
    monkeypatch.setattr(settings, "apple_client_secret", type(settings.apple_client_secret)("apple-secret"))
    monkeypatch.setattr(settings, "cookie_secure", False)

    status = oauth_provider_status()
    assert status["google"]["available"] is True
    assert status["facebook"]["available"] is True
    assert status["apple"]["configured"] is True
    assert status["apple"]["available"] is False
    assert "HTTPS" in status["apple"]["reason"]
