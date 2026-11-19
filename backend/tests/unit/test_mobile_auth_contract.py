from app.schemas.auth import (
    MobileExchangeRequest,
    MobileLoginRequest,
    MobileLogoutRequest,
    MobileRefreshRequest,
    MobileTokenResponse,
    UserOut,
)


def test_mobile_login_request_validates_email_and_password():
    payload = MobileLoginRequest(email="shopper@example.com", password="secret")
    assert payload.email == "shopper@example.com"


def test_mobile_exchange_code_requires_nontrivial_one_time_code():
    payload = MobileExchangeRequest(code="x" * 32)
    assert len(payload.code) == 32


def test_mobile_refresh_and_logout_payloads():
    refresh = MobileRefreshRequest(refresh_token="r" * 40)
    logout = MobileLogoutRequest(access_token="a" * 40, refresh_token=refresh.refresh_token)
    assert logout.refresh_token == refresh.refresh_token


def test_mobile_response_contract_contains_tokens_and_user():
    response = MobileTokenResponse(
        access_token="access-token",
        refresh_token="refresh-token",
        expires_in=900,
        refresh_expires_in=1209600,
        user=UserOut(
            id="00000000-0000-0000-0000-000000000001",
            name="NOVA Customer",
            email="shopper@example.com",
            phone="+201000000000",
            whatsapp_opt_in=False,
            email_verified=True,
            role="customer",
        ),
    )
    assert response.token_type == "Bearer"
    assert response.user.role == "customer"


def test_mobile_token_response_uses_the_server_token_pair():
    import pytest
    pytest.importorskip("redis")
    from uuid import uuid4

    from app.api.v1.auth import mobile_token_response
    from app.models import User

    user = User(
        id=uuid4(), name="NOVA Mobile", email="mobile@example.com", phone="+201000000000",
        whatsapp_opt_in=False, email_verified=True, is_active=True, role="customer",
    )
    pair = {
        "access": ("access.jwt.value", "access-jti", 1234567890),
        "refresh": ("refresh.jwt.value", "refresh-jti", 1234567899),
    }
    response = mobile_token_response(user, pair)
    assert response.access_token == "access.jwt.value"
    assert response.refresh_token == "refresh.jwt.value"
    assert response.user.id == user.id
    assert response.user.role == "customer"
