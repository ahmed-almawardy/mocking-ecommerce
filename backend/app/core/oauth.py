"""OAuth client registration for supported customer identity providers."""

from authlib.integrations.starlette_client import OAuth

from app.core.config import get_settings

settings = get_settings()
oauth = OAuth()

if settings.google_client_id and settings.google_client_secret.get_secret_value():
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret.get_secret_value(),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

if settings.facebook_client_id and settings.facebook_client_secret.get_secret_value():
    graph_base = f"https://graph.facebook.com/{settings.facebook_graph_version}/"
    oauth.register(
        name="facebook",
        client_id=settings.facebook_client_id,
        client_secret=settings.facebook_client_secret.get_secret_value(),
        authorize_url=f"https://www.facebook.com/{settings.facebook_graph_version}/dialog/oauth",
        access_token_url=f"{graph_base}oauth/access_token",
        api_base_url=graph_base,
        client_kwargs={"scope": "email,public_profile"},
    )

if settings.apple_client_id and settings.apple_client_secret.get_secret_value():
    oauth.register(
        name="apple",
        client_id=settings.apple_client_id,
        client_secret=settings.apple_client_secret.get_secret_value(),
        server_metadata_url="https://appleid.apple.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email name", "response_mode": "form_post"},
    )
