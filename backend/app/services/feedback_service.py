import uuid
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.models.models import (
    Feedback,
    Priority,
    SLAStatus,
    Ticket,
    TicketLog,
    TicketStatus,
)
from app.schemas.schemas import (
    FeedbackCreate,
    FeedbackFilter,
    TicketCreate,
    TicketUpdate,
)


def _generate_id(prefix: str) -> str:
    return f"{prefix}{uuid.uuid4().hex[:8].upper()}"


def _get_sla_minutes(priority: Priority | str) -> tuple[int, int]:
    """Return (response_minutes, resolve_minutes) for a given priority."""
    p = priority.value if isinstance(priority, Priority) else priority
    mapping = {
        "P0": (settings.SLA_P0_RESPONSE, settings.SLA_P0_RESOLVE),
        "P1": (settings.SLA_P1_RESPONSE, settings.SLA_P1_RESOLVE),
        "P2": (settings.SLA_P2_RESPONSE, settings.SLA_P2_RESOLVE),
        "P3": (settings.SLA_P3_RESPONSE, settings.SLA_P3_RESOLVE),
    }
    return mapping[p]


def _enum_val(v):
    """Extract .value from enum, or return as-is if already a string."""
    return v.value if hasattr(v, "value") else v


# --- Feedback Service ---


async def create_feedback(db: AsyncSession, data: FeedbackCreate) -> Feedback:
    dump = data.model_dump()
    # Convert enum values to strings for SQLite-compatible String columns
    for key in ("source",):
        if key in dump and hasattr(dump[key], "value"):
            dump[key] = dump[key].value
    feedback = Feedback(
        feedback_id=_generate_id("F"),
        **dump,
    )
    db.add(feedback)
    await db.flush()
    return feedback


async def get_feedback(db: AsyncSession, feedback_id: str) -> Feedback | None:
    stmt = (
        select(Feedback)
        .options(joinedload(Feedback.ticket).joinedload(Ticket.logs))
        .where(Feedback.feedback_id == feedback_id)
    )
    result = await db.execute(stmt)
    return result.unique().scalar_one_or_none()


async def list_feedbacks(
    db: AsyncSession, filters: FeedbackFilter
) -> tuple[list[Feedback], int]:
    stmt = select(Feedback).options(joinedload(Feedback.ticket))

    # Apply filters
    if filters.rating_min is not None:
        stmt = stmt.where(Feedback.rating >= filters.rating_min)
    if filters.rating_max is not None:
        stmt = stmt.where(Feedback.rating <= filters.rating_max)
    if filters.time_start is not None:
        stmt = stmt.where(Feedback.feedback_time >= filters.time_start)
    if filters.time_end is not None:
        stmt = stmt.where(Feedback.feedback_time <= filters.time_end)
    if filters.city:
        stmt = stmt.where(Feedback.city == filters.city)
    if filters.route:
        stmt = stmt.where(Feedback.route.ilike(f"%{filters.route}%"))
    if filters.source:
        stmt = stmt.where(Feedback.source == _enum_val(filters.source))
    if filters.ai_category:
        stmt = stmt.where(Feedback.ai_category == _enum_val(filters.ai_category))
    if filters.priority:
        stmt = stmt.where(Feedback.ticket.has(Ticket.priority == _enum_val(filters.priority)))
    if filters.ticket_status:
        stmt = stmt.where(Feedback.ticket.has(Ticket.status == _enum_val(filters.ticket_status)))

    # Count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    # Sort
    sort_col = getattr(Feedback, filters.sort_by, Feedback.feedback_time)
    if filters.sort_order == "asc":
        stmt = stmt.order_by(sort_col.asc())
    else:
        stmt = stmt.order_by(sort_col.desc())

    # Paginate
    offset = (filters.page - 1) * filters.page_size
    stmt = stmt.offset(offset).limit(filters.page_size)

    result = await db.execute(stmt)
    items = list(result.unique().scalars().all())
    return items, total


async def get_feedbacks_by_user(db: AsyncSession, user_id: str) -> list[Feedback]:
    stmt = (
        select(Feedback)
        .options(joinedload(Feedback.ticket))
        .where(Feedback.user_id == user_id)
        .order_by(Feedback.feedback_time.desc())
    )
    result = await db.execute(stmt)
    return list(result.unique().scalars().all())


async def get_feedbacks_by_vehicle(db: AsyncSession, vehicle_id: str) -> list[Feedback]:
    stmt = (
        select(Feedback)
        .options(joinedload(Feedback.ticket))
        .where(Feedback.vehicle_id == vehicle_id)
        .order_by(Feedback.feedback_time.desc())
    )
    result = await db.execute(stmt)
    return list(result.unique().scalars().all())


# --- Ticket Service ---


async def create_ticket(db: AsyncSession, data: TicketCreate, operator: str) -> Ticket:
    # Find the feedback
    feedback = await get_feedback(db, data.feedback_id)
    if not feedback:
        raise ValueError(f"Feedback {data.feedback_id} not found")
    if feedback.ticket_id is not None:
        raise ValueError(f"Feedback {data.feedback_id} already has a ticket")

    # Calculate SLA deadlines
    now = datetime.utcnow()
    response_min, resolve_min = _get_sla_minutes(data.priority)
    priority_str = _enum_val(data.priority)

    ticket = Ticket(
        ticket_id=_generate_id("TK"),
        priority=priority_str,
        status=TicketStatus.PENDING.value,
        assignee=data.assignee,
        sla_response_deadline=now + timedelta(minutes=response_min),
        sla_resolve_deadline=now + timedelta(minutes=resolve_min),
        sla_status=SLAStatus.NORMAL.value,
    )
    db.add(ticket)
    await db.flush()

    # Link feedback to ticket
    feedback.ticket_id = ticket.id

    # Create log
    log = TicketLog(
        ticket_pk=ticket.id,
        operator=operator,
        action="created",
        detail=f"工单创建，优先级 {priority_str}",
    )
    db.add(log)

    if data.assignee:
        assign_log = TicketLog(
            ticket_pk=ticket.id,
            operator=operator,
            action="assigned",
            detail=f"分派给 {data.assignee}",
        )
        db.add(assign_log)

    await db.flush()
    return ticket


async def get_ticket(db: AsyncSession, ticket_id: str) -> Ticket | None:
    stmt = (
        select(Ticket)
        .options(joinedload(Ticket.feedback), joinedload(Ticket.logs))
        .where(Ticket.ticket_id == ticket_id)
    )
    result = await db.execute(stmt)
    return result.unique().scalar_one_or_none()


async def update_ticket(
    db: AsyncSession, ticket_id: str, data: TicketUpdate, operator: str
) -> Ticket:
    ticket = await get_ticket(db, ticket_id)
    if not ticket:
        raise ValueError(f"Ticket {ticket_id} not found")

    changes: list[str] = []

    if data.status is not None and _enum_val(data.status) != ticket.status:
        old_status = ticket.status
        new_status = _enum_val(data.status)
        ticket.status = new_status
        changes.append(f"状态从 {old_status} 变更为 {new_status}")
        if new_status == TicketStatus.RESOLVED.value:
            ticket.resolved_time = datetime.utcnow()

    if data.priority is not None and _enum_val(data.priority) != ticket.priority:
        old_priority = ticket.priority
        new_priority = _enum_val(data.priority)
        ticket.priority = new_priority
        # Recalculate SLA
        now = datetime.utcnow()
        response_min, resolve_min = _get_sla_minutes(new_priority)
        ticket.sla_response_deadline = now + timedelta(minutes=response_min)
        ticket.sla_resolve_deadline = now + timedelta(minutes=resolve_min)
        ticket.sla_status = SLAStatus.NORMAL.value
        changes.append(f"优先级从 {old_priority} 变更为 {new_priority}")

    if data.assignee is not None and data.assignee != ticket.assignee:
        old_assignee = ticket.assignee or "未分派"
        ticket.assignee = data.assignee
        changes.append(f"负责人从 {old_assignee} 变更为 {data.assignee}")

    if data.processing_result is not None:
        result_str = _enum_val(data.processing_result)
        ticket.processing_result = result_str
        changes.append(f"处理方式: {result_str}")

    if data.processing_note is not None:
        ticket.processing_note = data.processing_note
        changes.append("更新了处理备注")

    if changes:
        log = TicketLog(
            ticket_pk=ticket.id,
            operator=operator,
            action="updated",
            detail="；".join(changes),
        )
        db.add(log)

    await db.flush()
    return ticket


async def list_tickets(
    db: AsyncSession,
    status: TicketStatus | None = None,
    priority: Priority | None = None,
    assignee: str | None = None,
    sla_status: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Ticket], int]:
    stmt = select(Ticket).options(joinedload(Ticket.feedback), joinedload(Ticket.logs))

    if status:
        stmt = stmt.where(Ticket.status == _enum_val(status))
    if priority:
        stmt = stmt.where(Ticket.priority == _enum_val(priority))
    if assignee:
        stmt = stmt.where(Ticket.assignee == assignee)
    if sla_status:
        stmt = stmt.where(Ticket.sla_status == sla_status)

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0

    stmt = stmt.order_by(Ticket.created_at.desc())
    offset = (page - 1) * page_size
    stmt = stmt.offset(offset).limit(page_size)

    result = await db.execute(stmt)
    items = list(result.unique().scalars().all())
    return items, total
