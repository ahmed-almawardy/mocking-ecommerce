import re

import httpx

from app.core.config import get_settings


class WhatsAppError(RuntimeError):
    pass


async def _send_template(payload: dict) -> None:
    settings = get_settings()
    if not settings.whatsapp_enabled:
        return
    if not settings.whatsapp_access_token.get_secret_value() or not settings.whatsapp_phone_number_id:
        raise WhatsAppError("WhatsApp Cloud API credentials are incomplete")
    url = f"https://graph.facebook.com/{settings.whatsapp_graph_version}/{settings.whatsapp_phone_number_id}/messages"
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(
            url,
            headers={"Authorization": f"Bearer {settings.whatsapp_access_token.get_secret_value()}", "Content-Type": "application/json"},
            json=payload,
        )
    if response.is_error:
        raise WhatsAppError(f"WhatsApp API rejected the message ({response.status_code})")


def _whatsapp_recipient(phone: str) -> str:
    # WhatsApp Cloud API expects a country-code number without punctuation.
    digits = re.sub(r"\D", "", phone)
    if not digits:
        raise WhatsAppError("Recipient phone number is invalid")
    # Accept common Egyptian local formats and convert them to international country-code form.
    if len(digits) == 11 and digits.startswith("01"):
        digits = "20" + digits[1:]
    elif len(digits) == 10 and digits.startswith(("10", "11", "12", "15")):
        digits = "20" + digits
    return digits


async def send_welcome(phone: str, name: str) -> None:
    settings = get_settings()
    await _send_template({
        "messaging_product": "whatsapp",
        "to": _whatsapp_recipient(phone),
        "type": "template",
        "template": {
            "name": settings.whatsapp_welcome_template,
            "language": {"code": settings.whatsapp_template_language},
            "components": [{"type": "body", "parameters": [{"type": "text", "text": name}]}],
        },
    })


async def upload_pdf_and_send_receipt(phone: str, pdf_path: str, order_number: str, total: str) -> None:
    settings = get_settings()
    if not settings.whatsapp_enabled:
        return
    base = f"https://graph.facebook.com/{settings.whatsapp_graph_version}/{settings.whatsapp_phone_number_id}"
    headers = {"Authorization": f"Bearer {settings.whatsapp_access_token.get_secret_value()}"}
    async with httpx.AsyncClient(timeout=40) as client:
        with open(pdf_path, "rb") as pdf_file:
            media_response = await client.post(
                f"{base}/media",
                headers=headers,
                data={"messaging_product": "whatsapp", "type": "application/pdf"},
                files={"file": (f"receipt-{order_number}.pdf", pdf_file, "application/pdf")},
            )
        if media_response.is_error:
            raise WhatsAppError("WhatsApp media upload failed")
        media_id = media_response.json().get("id")
        if not media_id:
            raise WhatsAppError("WhatsApp media upload returned no media id")
        payload = {
            "messaging_product": "whatsapp", "to": _whatsapp_recipient(phone), "type": "template",
            "template": {
                "name": settings.whatsapp_receipt_template,
                "language": {"code": settings.whatsapp_template_language},
                "components": [
                    {"type": "header", "parameters": [{"type": "document", "document": {"id": media_id, "filename": f"receipt-{order_number}.pdf"}}]},
                    {"type": "body", "parameters": [
                        {"type": "text", "text": order_number},
                        {"type": "text", "text": total},
                    ]},
                ],
            },
        }
        response = await client.post(f"{base}/messages", headers={**headers, "Content-Type": "application/json"}, json=payload)
        if response.is_error:
            raise WhatsAppError("WhatsApp receipt template send failed")
