import pytest
from app.services.auth import normalize_phone, resolve_oauth_identity


@pytest.mark.asyncio
async def test_oauth_existing_email_requires_verified_claim():
    class ExistingUser:
        id = "existing-user"
    class FakeDB:
        def __init__(self):
            self.added = []
        async def scalar(self, statement):
            from app.models import AuthIdentity
            entity = statement.column_descriptions[0]["entity"]
            return None if entity is AuthIdentity else ExistingUser()
        def add(self, value):
            self.added.append(value)
        async def commit(self):
            pass
        async def refresh(self, value):
            pass
    db = FakeDB()
    with pytest.raises(ValueError, match="already has an account"):
        await resolve_oauth_identity(db, provider="facebook", subject="fb-1", email="buyer@example.com", name="Buyer", email_verified=False)


def test_phone_normalization_uses_egypt_country_code_for_local_mobile():
    assert normalize_phone("010 1234 5678") == "+201012345678"
    assert normalize_phone("+20 101 234 5678") == "+201012345678"


def test_phone_normalization_rejects_invalid_number():
    with pytest.raises(ValueError, match="valid phone number"):
        normalize_phone("not-a-number")
