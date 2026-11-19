from app.db.base import Base
from app.models import Offer, PaymentTransaction, ProductEvent, User


def test_admin_and_analytics_tables_are_registered_in_metadata():
    assert {"offers", "product_events", "payment_transactions"}.issubset(Base.metadata.tables)
    assert User.__table__.c.role.server_default.arg == "customer"
    assert Offer.__table__.c.title_ar.nullable
    assert ProductEvent.__table__.c.event_type.type.length == 24
    assert PaymentTransaction.__table__.c.order_id.unique is True
