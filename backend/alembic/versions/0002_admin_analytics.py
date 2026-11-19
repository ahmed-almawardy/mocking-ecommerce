"""Admin dashboard, offers, payment records and product analytics.

Revision ID: 0002_admin_analytics
Revises: 0001_initial_schema
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_admin_analytics"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=24), server_default="customer", nullable=False))
    op.create_index("ix_users_role", "users", ["role"], unique=False)

    op.create_table(
        "offers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("subtitle", sa.String(length=300), server_default="", nullable=False),
        sa.Column("title_ar", sa.String(length=180), nullable=True),
        sa.Column("subtitle_ar", sa.String(length=300), nullable=True),
        sa.Column("image_url", sa.String(length=700), nullable=False),
        sa.Column("link_url", sa.String(length=700), server_default="/en/products", nullable=False),
        sa.Column("badge", sa.String(length=60), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_offers_is_active", "offers", ["is_active"], unique=False)

    op.create_table(
        "product_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_type", sa.String(length=24), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="1", nullable=False),
        sa.Column("session_key", sa.String(length=80), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_product_events_product_id", "product_events", ["product_id"], unique=False)
    op.create_index("ix_product_events_user_id", "product_events", ["user_id"], unique=False)
    op.create_index("ix_product_events_event_type", "product_events", ["event_type"], unique=False)
    op.create_index("ix_product_events_session_key", "product_events", ["session_key"], unique=False)
    op.create_index("ix_product_events_created_at", "product_events", ["created_at"], unique=False)

    op.create_table(
        "payment_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(length=40), server_default="kashier", nullable=False),
        sa.Column("reference", sa.String(length=180), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), server_default="EGP", nullable=False),
        sa.Column("method", sa.String(length=80), nullable=True),
        sa.Column("provider_transaction_id", sa.String(length=180), nullable=True),
        sa.Column("last_event_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference"),
    )
    op.create_index("ix_payment_transactions_order_id", "payment_transactions", ["order_id"], unique=True)
    op.create_index("ix_payment_transactions_status", "payment_transactions", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_payment_transactions_status", table_name="payment_transactions")
    op.drop_index("ix_payment_transactions_order_id", table_name="payment_transactions")
    op.drop_table("payment_transactions")
    op.drop_index("ix_product_events_created_at", table_name="product_events")
    op.drop_index("ix_product_events_session_key", table_name="product_events")
    op.drop_index("ix_product_events_event_type", table_name="product_events")
    op.drop_index("ix_product_events_user_id", table_name="product_events")
    op.drop_index("ix_product_events_product_id", table_name="product_events")
    op.drop_table("product_events")
    op.drop_index("ix_offers_is_active", table_name="offers")
    op.drop_table("offers")
    op.drop_index("ix_users_role", table_name="users")
    op.drop_column("users", "role")
