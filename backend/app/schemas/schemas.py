from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.models.models import (
    FeedbackCategory,
    FeedbackSource,
    Priority,
    ProcessingResult,
    TicketStatus,
)


# --- Feedback Schemas ---


class FeedbackBase(BaseModel):
    user_id: str
    trip_id: str
    vehicle_id: str
    rating: int = Field(ge=1, le=5)
    feedback_text: str
    city: str
    route: str
    trip_time: datetime
    trip_duration: int
    feedback_time: datetime
    source: FeedbackSource = FeedbackSource.APP_RATING


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackResponse(BaseModel):
    feedback_id: str
    user_id: str
    trip_id: str
    vehicle_id: str
    rating: int
    feedback_text: str
    city: str
    route: str
    trip_time: datetime
    trip_duration: int
    feedback_time: datetime
    source: str
    ai_category: str | None = None
    ai_confidence: float | None = None
    ai_status: str = "pending"
    cluster_id: str | None = None
    ticket_id: int | None = None
    ticket_biz_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @model_validator(mode="before")
    @classmethod
    def _fill_ticket_biz_id(cls, data):
        if hasattr(data, "ticket") and data.ticket is not None:
            ticket = data.ticket
            if hasattr(ticket, "ticket_id"):
                d = {
                    c.key: getattr(data, c.key)
                    for c in data.__class__.__table__.columns
                }
                d["ticket_biz_id"] = ticket.ticket_id
                return d
        return data


class FeedbackListResponse(BaseModel):
    items: list[FeedbackResponse]
    total: int
    page: int
    page_size: int


class FeedbackFilter(BaseModel):
    rating_min: int | None = None
    rating_max: int | None = None
    time_start: datetime | None = None
    time_end: datetime | None = None
    city: str | None = None
    route: str | None = None
    source: str | None = None
    ai_category: str | None = None
    ticket_status: str | None = None
    priority: str | None = None
    sort_by: str = "feedback_time"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 20


# --- Ticket Schemas ---


class TicketCreate(BaseModel):
    feedback_id: str  # the feedback's business ID
    priority: Priority
    assignee: str | None = None


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    priority: Priority | None = None
    assignee: str | None = None
    processing_result: ProcessingResult | None = None
    processing_note: str | None = None


class TicketLogResponse(BaseModel):
    operator: str
    action: str
    detail: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketResponse(BaseModel):
    ticket_id: str
    priority: str
    status: str
    assignee: str | None = None
    sla_response_deadline: datetime | None = None
    sla_resolve_deadline: datetime | None = None
    sla_status: str
    escalated: bool
    processing_result: str | None = None
    processing_note: str | None = None
    resolved_time: datetime | None = None
    feedback: FeedbackResponse | None = None
    logs: list[TicketLogResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TicketListResponse(BaseModel):
    items: list[TicketResponse]
    total: int
    page: int
    page_size: int


class TicketBatchCreate(BaseModel):
    feedback_ids: list[str]
    priority: Priority
    assignee: str | None = None


class TicketBatchAssign(BaseModel):
    ticket_ids: list[str]
    assignee: str


# --- Dashboard Schemas ---


class DashboardOverview(BaseModel):
    total_feedbacks: int
    total_today: int
    total_this_week: int
    total_this_month: int
    avg_rating: float
    positive_rate: float  # rating >= 4
    negative_rate: float  # rating <= 2
    open_tickets: int
    sla_compliance_rate: float


class TrendPoint(BaseModel):
    date: str
    value: float


class TrendData(BaseModel):
    negative_count: list[TrendPoint]
    positive_rate: list[TrendPoint]
    avg_rating: list[TrendPoint]


class DistributionItem(BaseModel):
    label: str
    count: int
    percentage: float


class DistributionData(BaseModel):
    by_rating: list[DistributionItem]
    by_route: list[DistributionItem]
    by_city: list[DistributionItem]
    by_category: list[DistributionItem]
    by_time_period: list[DistributionItem]


class TicketMetrics(BaseModel):
    by_priority: list[DistributionItem]
    avg_resolve_time_hours: dict[str, float]  # priority -> hours
    sla_compliance_by_priority: dict[str, float]  # priority -> rate
    open_tickets_aging: list[DistributionItem]  # <1d, 1-3d, 3-7d, >7d


class RouteTrendSeries(BaseModel):
    route: str
    data: list[int]


class RouteTrendData(BaseModel):
    dates: list[str]
    series: list[RouteTrendSeries]


# --- AI Analysis Schemas ---


class AIAnalyzeRequest(BaseModel):
    feedback_ids: list[str] = Field(..., min_length=1, max_length=100)


class AIAnalyzeSummary(BaseModel):
    major_problems: list[str]
    feedback_themes: list[str]
    action_suggestions: list[str]
    trend_summary: str


class AIAnalyzeResponse(BaseModel):
    summary: AIAnalyzeSummary
    feedback_count: int


class DashboardReportRequest(BaseModel):
    period: Literal["daily", "weekly", "monthly"]


class DashboardReportResponse(BaseModel):
    report: str
    period: str
    generated_at: str


# --- Auth Schemas ---


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    username: str
    display_name: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}
