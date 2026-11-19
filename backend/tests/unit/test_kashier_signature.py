from app.services.payments.kashier import build_webhook_signature, verify_webhook_signature


def test_signature_is_deterministic_and_validated():
    data = {
        "amount": "150.00",
        "status": "SUCCESS",
        "transactionId": "TX-123",
        "signatureKeys": ["transactionId", "status", "amount"],
    }
    signature = build_webhook_signature(data, "test-payment-api-key")
    assert verify_webhook_signature(data, signature, "test-payment-api-key")
    assert not verify_webhook_signature(data, "wrong", "test-payment-api-key")
    assert not verify_webhook_signature(data, signature, "different-key")
