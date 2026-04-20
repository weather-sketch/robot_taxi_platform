"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-04-18
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Ticket ---
    op.create_table(
        "ticket",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ticket_id", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("priority", sa.String(4), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("assignee", sa.String(64), nullable=True, index=True),
        sa.Column("sla_response_deadline", sa.DateTime, nullable=True),
        sa.Column("sla_resolve_deadline", sa.DateTime, nullable=True),
        sa.Column("sla_status", sa.String(16), nullable=False, server_default="normal"),
        sa.Column("escalated", sa.Boolean, nullable=False, server_default=sa.text("0")),
        sa.Column("processing_result", sa.String(16), nullable=True),
        sa.Column("processing_note", sa.Text, nullable=True),
        sa.Column("resolved_time", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- Feedback ---
    op.create_table(
        "feedback",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("feedback_id", sa.String(32), unique=True, nullable=False, index=True),
        sa.Column("user_id", sa.String(64), nullable=False, index=True),
        sa.Column("trip_id", sa.String(64), nullable=False),
        sa.Column("vehicle_id", sa.String(64), nullable=False, index=True),
        sa.Column("rating", sa.Integer, nullable=False),
        sa.Column("feedback_text", sa.Text, nullable=False),
        sa.Column("city", sa.String(32), nullable=False, index=True),
        sa.Column("route", sa.String(128), nullable=False),
        sa.Column("trip_time", sa.DateTime, nullable=False),
        sa.Column("trip_duration", sa.Integer, nullable=False),
        sa.Column("feedback_time", sa.DateTime, nullable=False, index=True),
        sa.Column("source", sa.String(32), nullable=False, server_default="app_rating"),
        sa.Column("ai_category", sa.String(32), nullable=True),
        sa.Column("ai_confidence", sa.Float, nullable=True),
        sa.Column("ai_status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("cluster_id", sa.String(32), nullable=True),
        sa.Column("ticket_id", sa.Integer, sa.ForeignKey("ticket.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- Ticket Log ---
    op.create_table(
        "ticket_log",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ticket_pk", sa.Integer, sa.ForeignKey("ticket.id"), nullable=False),
        sa.Column("operator", sa.String(64), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("detail", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- User Account ---
    op.create_table(
        "user_account",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(64), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(256), nullable=False),
        sa.Column("display_name", sa.String(64), nullable=False),
        sa.Column("role", sa.String(16), nullable=False, server_default="operator"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- Notification Log ---
    op.create_table(
        "notification_log",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("ticket_pk", sa.Integer, sa.ForeignKey("ticket.id"), nullable=True),
        sa.Column("recipient", sa.String(64), nullable=False),
        sa.Column("channel", sa.String(32), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("sent_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    # --- Social Signal ---
    op.create_table(
        "social_signal",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("platform", sa.String(32), nullable=False),
        sa.Column("content_summary", sa.Text, nullable=False),
        sa.Column("sentiment", sa.String(16), nullable=False),
        sa.Column("heat_score", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("original_url", sa.String(512), nullable=True),
        sa.Column("captured_at", sa.DateTime, nullable=False),
        sa.Column(
            "linked_feedback_id", sa.Integer, sa.ForeignKey("feedback.id"), nullable=True
        ),
        sa.Column(
            "linked_ticket_id", sa.Integer, sa.ForeignKey("ticket.id"), nullable=True
        ),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade() -> None:
    op.drop_table("social_signal")
    op.drop_table("notification_log")
    op.drop_table("user_account")
    op.drop_table("ticket_log")
    op.drop_table("feedback")
    op.drop_table("ticket")
