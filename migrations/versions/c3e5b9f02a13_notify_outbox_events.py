"""Add notify_outbox_events table

Revision ID: c3e5b9f02a13
Revises: b2d4a8e91f22
Create Date: 2026-09-04

Durable outbox for site -> Telegram-bot notifications (see
app/models::NotifyOutboxEvent, app/services/notify_outbox_service.py).
Replaces BotNotifyService's old fully-synchronous "POST and hope" — an
event is now persisted here first and delivered (with retries/backoff) by
a separate drain step, so bot downtime never blocks the request that
triggered the notification and a transient failure is retried instead of
silently dropped.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c3e5b9f02a13"
down_revision = "b2d4a8e91f22"
branch_labels = None
depends_on = None


def upgrade():
    outbox_status = sa.Enum(
        "pending", "processing", "delivered", "failed",
        name="outbox_event_status_enum",
    )
    op.create_table(
        "notify_outbox_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(length=36), nullable=False, unique=True),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("status", outbox_status, nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="8"),
        sa.Column("next_attempt_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_notify_outbox_events_status_next_attempt",
        "notify_outbox_events", ["status", "next_attempt_at"],
    )


def downgrade():
    op.drop_index("ix_notify_outbox_events_status_next_attempt", table_name="notify_outbox_events")
    op.drop_table("notify_outbox_events")
    sa.Enum(name="outbox_event_status_enum").drop(op.get_bind(), checkfirst=True)
