import pytest

from app.services.notifications.whatsapp import WhatsAppError, _whatsapp_recipient


def test_egyptian_local_mobile_is_normalized_for_whatsapp():
    assert _whatsapp_recipient("010 1234 5678") == "201012345678"
    assert _whatsapp_recipient("+20 101 234 5678") == "201012345678"


def test_invalid_whatsapp_phone_is_rejected():
    with pytest.raises(WhatsAppError):
        _whatsapp_recipient("---")
