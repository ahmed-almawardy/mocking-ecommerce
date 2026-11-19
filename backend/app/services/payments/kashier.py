import hashlib
import hmac
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from urllib.parse import quote

import httpx

from app.core.config import get_settings


class KashierError(RuntimeError):
    pass


def build_webhook_signature(data: dict, payment_api_key: str) -> str:
    """Build the SHA256 HMAC described in Kashier's webhook documentation."""
    keys = sorted(data.get("signatureKeys") or [])
    if not keys:
        raise ValueError("Webhook payload is missing signatureKeys")
    payload = "&".join(f"{key}={quote(str(data.get(key, '')), safe='')}" for key in keys)
    return hmac.new(payment_api_key.encode(), payload.encode(), hashlib.sha256).hexdigest()


def verify_webhook_signature(data: dict, supplied_signature: str, payment_api_key: str) -> bool:
    if not supplied_signature or not payment_api_key:
        return False
    try:
        expected = build_webhook_signature(data, payment_api_key)
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(expected.lower(), supplied_signature.lower())


async def create_payment_session(*, order_number: str, amount: Decimal, customer_email: str, customer_id: str) -> str:
    settings = get_settings()
    if not all([settings.kashier_api_key, settings.kashier_secret_key.get_secret_value(), settings.kashier_merchant_id]):
        raise KashierError("Kashier credentials are not configured")
    expires = (datetime.now(UTC) + timedelta(hours=1)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    payload = {
        "expireAt": expires,
        "maxFailureAttempts": 3,
        "paymentType": settings.kashier_payment_type,
        "amount": f"{amount:.2f}",
        "currency": "EGP",
        "order": order_number,
        "merchantId": settings.kashier_merchant_id,
        "merchantRedirect": f"{settings.frontend_url.rstrip('/')}/checkout/complete?order={order_number}",
        "display": "en",
        "type": "one-time",
        "allowedMethods": "card,wallet",
        "customer": {"email": customer_email, "reference": customer_id},
        "serverWebhook": f"{settings.api_public_url.rstrip('/')}/api/v1/webhooks/kashier",
    }
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            response = await client.post(
                f"{settings.kashier_base_url}/v3/payment/sessions",
                headers={
                    "Authorization": settings.kashier_secret_key.get_secret_value(),
                    "api-key": settings.kashier_api_key,
                    "Content-Type": "application/json",
                },
                json=payload,
            )
    except httpx.HTTPError as exc:
        raise KashierError("Kashier could not be reached") from exc
    if response.is_error:
        raise KashierError(f"Kashier rejected the payment session ({response.status_code})")
    result = response.json()
    session_url = result.get("sessionUrl")
    if not session_url:
        raise KashierError("Kashier response did not include sessionUrl")
    return session_url
