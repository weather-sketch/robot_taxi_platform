"""seed data and default users

Revision ID: 002_seed_data
Revises: 001_initial
Create Date: 2026-04-18
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from passlib.context import CryptContext

revision: str = "002_seed_data"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DEFAULT_USERS = [
    ("admin", "admin123", "管理员", "admin"),
    ("supervisor01", "pass123", "运营主管-张华", "supervisor"),
    ("op01", "pass123", "运营-李明", "operator"),
    ("op02", "pass123", "运营-王芳", "operator"),
    ("analyst01", "pass123", "分析师-赵刚", "analyst"),
]


def upgrade() -> None:
    # --- Insert default users ---
    user_table = sa.table(
        "user_account",
        sa.column("username", sa.String),
        sa.column("hashed_password", sa.String),
        sa.column("display_name", sa.String),
        sa.column("role", sa.String),
        sa.column("is_active", sa.Boolean),
    )
    for username, password, display_name, role in DEFAULT_USERS:
        op.execute(
            user_table.insert().values(
                username=username,
                hashed_password=pwd_context.hash(password),
                display_name=display_name,
                role=role,
                is_active=True,
            )
        )

    # --- Load feedback seed data ---
    scripts_dir = Path(__file__).resolve().parent.parent.parent / "scripts"
    feedbacks_path = scripts_dir / "feedbacks.json"
    signals_path = scripts_dir / "social_signals.json"

    if feedbacks_path.exists():
        feedbacks = json.loads(feedbacks_path.read_text(encoding="utf-8"))
        _insert_feedbacks(feedbacks)

    if signals_path.exists():
        signals = json.loads(signals_path.read_text(encoding="utf-8"))
        _insert_signals(signals)


def _insert_feedbacks(feedbacks: list[dict]) -> None:
    ticket_table = sa.table(
        "ticket",
        sa.column("id", sa.Integer),
        sa.column("ticket_id", sa.String),
        sa.column("priority", sa.String),
        sa.column("status", sa.String),
        sa.column("assignee", sa.String),
        sa.column("sla_response_deadline", sa.DateTime),
        sa.column("sla_resolve_deadline", sa.DateTime),
        sa.column("sla_status", sa.String),
        sa.column("escalated", sa.Boolean),
        sa.column("processing_result", sa.String),
        sa.column("processing_note", sa.String),
        sa.column("resolved_time", sa.DateTime),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    feedback_table = sa.table(
        "feedback",
        sa.column("feedback_id", sa.String),
        sa.column("user_id", sa.String),
        sa.column("trip_id", sa.String),
        sa.column("vehicle_id", sa.String),
        sa.column("rating", sa.Integer),
        sa.column("feedback_text", sa.String),
        sa.column("city", sa.String),
        sa.column("route", sa.String),
        sa.column("trip_time", sa.DateTime),
        sa.column("trip_duration", sa.Integer),
        sa.column("feedback_time", sa.DateTime),
        sa.column("source", sa.String),
        sa.column("ai_category", sa.String),
        sa.column("ai_confidence", sa.Float),
        sa.column("ai_status", sa.String),
        sa.column("cluster_id", sa.String),
        sa.column("ticket_id", sa.Integer),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    ticket_log_table = sa.table(
        "ticket_log",
        sa.column("ticket_pk", sa.Integer),
        sa.column("operator", sa.String),
        sa.column("action", sa.String),
        sa.column("detail", sa.String),
    )

    ticket_counter = 0
    assignees = ["op01", "op02", "supervisor01"]
    now = datetime(2026, 4, 19)
    random.seed(123)

    processing_results = ["补偿", "技术问题", "无需处理", "其他"]

    for fb in feedbacks:
        created = datetime.fromisoformat(fb["created_at"])
        ticket_pk = None

        if fb.get("priority"):
            ticket_counter += 1
            ticket_id = f"TK{ticket_counter:05d}"
            assignee = assignees[ticket_counter % len(assignees)]

            age_days = (now - created).days

            if age_days > 14:
                status = random.choice(["closed"] * 7 + ["resolved"] * 3)
            elif age_days > 7:
                status = random.choice(
                    ["resolved"] * 4 + ["processing"] * 3 + ["closed"] * 2 + ["pending"]
                )
            elif age_days > 3:
                status = random.choice(
                    ["processing"] * 5 + ["pending"] * 3 + ["resolved"] * 2
                )
            else:
                status = random.choice(["pending"] * 6 + ["processing"] * 4)

            if status in ("resolved", "closed"):
                sla_status = random.choice(["normal"] * 8 + ["warning"] + ["overdue"])
            elif age_days > 7:
                sla_status = random.choice(["overdue"] * 6 + ["warning"] * 3 + ["normal"])
            elif age_days > 3:
                sla_status = random.choice(["warning"] * 5 + ["normal"] * 3 + ["overdue"] * 2)
            else:
                sla_status = random.choice(["normal"] * 7 + ["warning"] * 3)

            resolved_time = None
            processing_result = None
            processing_note = None
            if status in ("resolved", "closed"):
                resolve_hours = random.uniform(2, 48)
                resolved_time = created + timedelta(hours=resolve_hours)
                processing_result = random.choice(processing_results)
                notes = [
                    "已联系用户确认并处理", "已反馈至技术团队", "已发放补偿优惠券",
                    "已与用户沟通解释", "问题已定位并修复", "用户反馈已解决",
                    "已升级处理并关闭", "已安排专人跟进处理完成",
                ]
                processing_note = random.choice(notes)

            sla_mins = {"P0": (60, 240), "P1": (120, 480), "P2": (480, 2880), "P3": (1440, 10080)}
            resp_min, resolve_min = sla_mins.get(fb["priority"], (480, 2880))

            conn = op.get_bind()
            result = conn.execute(
                ticket_table.insert()
                .values(
                    ticket_id=ticket_id,
                    priority=fb["priority"],
                    status=status,
                    assignee=assignee,
                    sla_response_deadline=created + timedelta(minutes=resp_min),
                    sla_resolve_deadline=created + timedelta(minutes=resolve_min),
                    sla_status=sla_status,
                    escalated=sla_status == "overdue",
                    processing_result=processing_result,
                    processing_note=processing_note,
                    resolved_time=resolved_time,
                    created_at=created,
                    updated_at=resolved_time or created,
                )
                .returning(sa.column("id"))
            )
            ticket_pk = result.scalar()

            op.execute(
                ticket_log_table.insert().values(
                    ticket_pk=ticket_pk,
                    operator="system",
                    action="created",
                    detail=f"工单创建，优先级 {fb['priority']}",
                )
            )

            if status in ("processing", "resolved", "closed"):
                op.execute(
                    ticket_log_table.insert().values(
                        ticket_pk=ticket_pk,
                        operator=assignee,
                        action="updated",
                        detail="状态从 pending 变更为 processing",
                    )
                )

            if status in ("resolved", "closed"):
                op.execute(
                    ticket_log_table.insert().values(
                        ticket_pk=ticket_pk,
                        operator=assignee,
                        action="updated",
                        detail=f"状态从 processing 变更为 resolved；处理方式: {processing_result}",
                    )
                )

            if status == "closed":
                op.execute(
                    ticket_log_table.insert().values(
                        ticket_pk=ticket_pk,
                        operator="supervisor01",
                        action="updated",
                        detail="状态从 resolved 变更为 closed",
                    )
                )

        op.execute(
            feedback_table.insert().values(
                feedback_id=fb["feedback_id"],
                user_id=fb["user_id"],
                trip_id=fb["trip_id"],
                vehicle_id=fb["vehicle_id"],
                rating=fb["rating"],
                feedback_text=fb["feedback_text"],
                city=fb["city"],
                route=fb["route"],
                trip_time=datetime.fromisoformat(fb["trip_time"]),
                trip_duration=fb["trip_duration"],
                feedback_time=datetime.fromisoformat(fb["feedback_time"]),
                source=fb["source"],
                ai_category=fb.get("ai_category"),
                ai_confidence=fb.get("ai_confidence"),
                ai_status=fb.get("ai_status", "completed"),
                cluster_id=fb.get("cluster_id"),
                ticket_id=ticket_pk,
                created_at=created,
                updated_at=created,
            )
        )


def _insert_signals(signals: list[dict]) -> None:
    signal_table = sa.table(
        "social_signal",
        sa.column("platform", sa.String),
        sa.column("content_summary", sa.String),
        sa.column("sentiment", sa.String),
        sa.column("heat_score", sa.Integer),
        sa.column("original_url", sa.String),
        sa.column("captured_at", sa.DateTime),
    )

    for sig in signals:
        op.execute(
            signal_table.insert().values(
                platform=sig["platform"],
                content_summary=sig["content_summary"],
                sentiment=sig["sentiment"],
                heat_score=sig["heat_score"],
                original_url=sig.get("original_url"),
                captured_at=datetime.fromisoformat(sig["captured_at"]),
            )
        )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM social_signal"))
    conn.execute(sa.text("DELETE FROM ticket_log"))
    conn.execute(sa.text("DELETE FROM feedback"))
    conn.execute(sa.text("DELETE FROM ticket"))
    conn.execute(sa.text("DELETE FROM user_account"))
