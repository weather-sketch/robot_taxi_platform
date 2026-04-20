import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


# --- Enums ---


class FeedbackSource(str, enum.Enum):
    APP_RATING = "app_rating"
    APP_FEEDBACK = "app_feedback"
    CUSTOMER_SERVICE = "customer_service"
    SOCIAL_MEDIA = "social_media"


class FeedbackCategory(str, enum.Enum):
    DRIVING = "驾驶行为"
    PICKUP_EXPERIENCE = "接驾体验"
    VEHICLE_ENV = "车内环境"
    ROUTE = "路线规划"
    SAFETY = "安全感知"
    PRICING = "费用相关"
    ONBOARDING = "新用户引导"
    OTHER = "其他"


class Priority(str, enum.Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class TicketStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    RESOLVED = "resolved"
    CLOSED = "closed"


class SLAStatus(str, enum.Enum):
    NORMAL = "normal"
    WARNING = "warning"
    OVERDUE = "overdue"


class AIStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingResult(str, enum.Enum):
    COMPENSATION = "补偿"
    TECH_ISSUE = "技术问题"
    NO_ACTION = "无需处理"
    OTHER = "其他"


class UserRole(str, enum.Enum):
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    ANALYST = "analyst"
    ADMIN = "admin"


# --- Models ---
# Using String columns instead of Enum() for SQLite compatibility.
# Python-side enum validation is handled by Pydantic schemas.


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    feedback_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    trip_id: Mapped[str] = mapped_column(String(64), nullable=False)
    vehicle_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    feedback_text: Mapped[str] = mapped_column(Text, nullable=False)

    city: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    route: Mapped[str] = mapped_column(String(128), nullable=False)
    trip_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    trip_duration: Mapped[int] = mapped_column(Integer, nullable=False)  # seconds
    feedback_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    source: Mapped[str] = mapped_column(
        String(32), nullable=False, default=FeedbackSource.APP_RATING.value
    )

    # AI fields
    ai_category: Mapped[str | None] = mapped_column(String(32), nullable=True)
    ai_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    ai_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default=AIStatus.PENDING.value
    )
    cluster_id: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Ticket link (1:1)
    ticket_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("ticket.id"), nullable=True
    )
    ticket: Mapped["Ticket | None"] = relationship(back_populates="feedback", uselist=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )


class Ticket(Base):
    __tablename__ = "ticket"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)

    priority: Mapped[str] = mapped_column(String(4), nullable=False)
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default=TicketStatus.PENDING.value
    )
    assignee: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    sla_response_deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sla_resolve_deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sla_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default=SLAStatus.NORMAL.value
    )
    escalated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    processing_result: Mapped[str | None] = mapped_column(String(16), nullable=True)
    processing_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    feedback: Mapped["Feedback | None"] = relationship(back_populates="ticket", uselist=False)
    logs: Mapped[list["TicketLog"]] = relationship(back_populates="ticket", order_by="TicketLog.created_at")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )


class TicketLog(Base):
    __tablename__ = "ticket_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_pk: Mapped[int] = mapped_column(Integer, ForeignKey("ticket.id"), nullable=False)
    operator: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    ticket: Mapped["Ticket"] = relationship(back_populates="logs")


class UserAccount(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(
        String(16), nullable=False, default=UserRole.OPERATOR.value
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )


class NotificationLog(Base):
    __tablename__ = "notification_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_pk: Mapped[int | None] = mapped_column(Integer, ForeignKey("ticket.id"), nullable=True)
    recipient: Mapped[str] = mapped_column(String(64), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )


class SocialSignal(Base):
    """Lightweight social media signal from external sentiment platforms."""
    __tablename__ = "social_signal"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    platform: Mapped[str] = mapped_column(String(32), nullable=False)
    content_summary: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[str] = mapped_column(String(16), nullable=False)
    heat_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    original_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    linked_feedback_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("feedback.id"), nullable=True
    )
    linked_ticket_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("ticket.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
