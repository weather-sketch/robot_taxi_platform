from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.core.deps import get_current_user, require_permission
from app.models.models import Feedback as FeedbackModel, Priority, Ticket as TicketModel, TicketStatus, UserAccount
from app.schemas.schemas import (
    AIAnalyzeRequest,
    AIAnalyzeResponse,
    AIAnalyzeSummary,
    FeedbackCreate,
    FeedbackFilter,
    FeedbackListResponse,
    FeedbackResponse,
    TicketCreate,
    TicketListResponse,
    TicketResponse,
    TicketUpdate,
)
from app.services import ai_service, feedback_service

router = APIRouter()


# --- Feedback ---


@router.post("/feedbacks", response_model=FeedbackResponse, tags=["feedback"])
async def create_feedback(
    data: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("feedback:create")),
):
    feedback = await feedback_service.create_feedback(db, data)
    return feedback


@router.get("/feedbacks", response_model=FeedbackListResponse, tags=["feedback"])
async def list_feedbacks(
    rating_min: int | None = None,
    rating_max: int | None = None,
    time_start: str | None = None,
    time_end: str | None = None,
    city: str | None = None,
    route: str | None = None,
    source: str | None = None,
    ai_category: str | None = None,
    ticket_status: str | None = None,
    priority: str | None = None,
    sort_by: str = "feedback_time",
    sort_order: str = "desc",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("feedback:read")),
):
    filters = FeedbackFilter(
        rating_min=rating_min,
        rating_max=rating_max,
        time_start=time_start,
        time_end=time_end,
        city=city,
        route=route,
        source=source,
        ai_category=ai_category,
        ticket_status=ticket_status,
        priority=priority,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )
    items, total = await feedback_service.list_feedbacks(db, filters)
    return FeedbackListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/feedbacks/ids", tags=["feedback"])
async def list_feedback_ids(
    rating_min: int | None = None,
    rating_max: int | None = None,
    time_start: str | None = None,
    time_end: str | None = None,
    city: str | None = None,
    route: str | None = None,
    source: str | None = None,
    ai_category: str | None = None,
    ticket_status: str | None = None,
    priority: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("feedback:read")),
):
    """Return all feedback_ids matching the given filters (no pagination)."""
    filters = FeedbackFilter(
        rating_min=rating_min,
        rating_max=rating_max,
        time_start=time_start,
        time_end=time_end,
        city=city,
        route=route,
        source=source,
        ai_category=ai_category,
        ticket_status=ticket_status,
        priority=priority,
        page=1,
        page_size=100000,
    )
    items, total = await feedback_service.list_feedbacks(db, filters)
    return {"ids": [fb.feedback_id for fb in items], "total": total}


@router.get("/feedbacks/export", tags=["feedback"])
async def export_feedbacks(
    ids: str | None = None,
    rating_min: int | None = None,
    rating_max: int | None = None,
    time_start: str | None = None,
    time_end: str | None = None,
    city: str | None = None,
    route: str | None = None,
    source: str | None = None,
    ai_category: str | None = None,
    ticket_status: str | None = None,
    priority: str | None = None,
    sort_by: str = "feedback_time",
    sort_order: str = "desc",
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("dashboard:export")),
):
    if ids:
        id_list = [x.strip() for x in ids.split(",") if x.strip()]
        stmt = (
            select(FeedbackModel)
            .options(joinedload(FeedbackModel.ticket))
            .where(FeedbackModel.feedback_id.in_(id_list))
        )
        result = await db.execute(stmt)
        items = result.unique().scalars().all()
    else:
        filters = FeedbackFilter(
            rating_min=rating_min,
            rating_max=rating_max,
            time_start=time_start,
            time_end=time_end,
            city=city,
            route=route,
            source=source,
            ai_category=ai_category,
            ticket_status=ticket_status,
            priority=priority,
            sort_by=sort_by,
            sort_order=sort_order,
            page=1,
            page_size=10000,
        )
        items, _ = await feedback_service.list_feedbacks(db, filters)

    wb = Workbook()
    ws = wb.active
    ws.title = "反馈数据"
    headers = ["反馈ID", "用户ID", "评分", "反馈内容", "分类", "城市", "路线", "来源", "工单号", "反馈时间"]
    ws.append(headers)
    for fb in items:
        ws.append([
            fb.feedback_id,
            fb.user_id,
            fb.rating,
            fb.feedback_text,
            fb.ai_category or "",
            fb.city,
            fb.route,
            fb.source,
            fb.ticket.ticket_id if fb.ticket else "",
            fb.feedback_time.strftime("%Y-%m-%d %H:%M") if fb.feedback_time else "",
        ])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=feedbacks.xlsx"},
    )


@router.post("/feedbacks/ai-analyze", response_model=AIAnalyzeResponse, tags=["feedback"])
async def ai_analyze_feedbacks(
    data: AIAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("ai:analyze")),
):
    stmt = (
        select(FeedbackModel)
        .options(joinedload(FeedbackModel.ticket))
        .where(FeedbackModel.feedback_id.in_(data.feedback_ids))
    )
    result = await db.execute(stmt)
    items = result.unique().scalars().all()

    if not items:
        raise HTTPException(status_code=404, detail="No feedbacks found for given IDs")

    feedback_dicts = [
        {
            "rating": fb.rating,
            "ai_category": fb.ai_category,
            "city": fb.city,
            "route": fb.route,
            "feedback_text": fb.feedback_text,
        }
        for fb in items
    ]

    try:
        raw = await ai_service.analyze_feedbacks(feedback_dicts)
        summary = AIAnalyzeSummary(**raw)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {e}")

    return AIAnalyzeResponse(summary=summary, feedback_count=len(items))


@router.get("/feedbacks/{feedback_id}", response_model=FeedbackResponse, tags=["feedback"])
async def get_feedback(
    feedback_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("feedback:read")),
):
    feedback = await feedback_service.get_feedback(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback


@router.get("/feedbacks/by-user/{user_id}", response_model=list[FeedbackResponse], tags=["feedback"])
async def get_feedbacks_by_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("feedback:read")),
):
    return await feedback_service.get_feedbacks_by_user(db, user_id)


@router.get(
    "/feedbacks/by-vehicle/{vehicle_id}",
    response_model=list[FeedbackResponse],
    tags=["feedback"],
)
async def get_feedbacks_by_vehicle(
    vehicle_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("feedback:read")),
):
    return await feedback_service.get_feedbacks_by_vehicle(db, vehicle_id)


# --- Tickets ---


@router.post("/tickets", response_model=TicketResponse, tags=["ticket"])
async def create_ticket(
    data: TicketCreate,
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("ticket:create")),
):
    try:
        ticket = await feedback_service.create_ticket(db, data, operator=user.username)
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tickets", response_model=TicketListResponse, tags=["ticket"])
async def list_tickets(
    status: TicketStatus | None = None,
    priority: Priority | None = None,
    assignee: str | None = None,
    sla_status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("ticket:read")),
):
    items, total = await feedback_service.list_tickets(
        db, status=status, priority=priority, assignee=assignee,
        sla_status=sla_status, page=page, page_size=page_size
    )
    return TicketListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/tickets/export", tags=["ticket"])
async def export_tickets(
    ids: str | None = None,
    status: TicketStatus | None = None,
    priority: Priority | None = None,
    assignee: str | None = None,
    sla_status: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("dashboard:export")),
):
    if ids:
        id_list = [x.strip() for x in ids.split(",") if x.strip()]
        stmt = (
            select(TicketModel)
            .options(joinedload(TicketModel.feedback))
            .where(TicketModel.ticket_id.in_(id_list))
        )
        result = await db.execute(stmt)
        items = result.unique().scalars().all()
    else:
        items, _ = await feedback_service.list_tickets(
            db, status=status, priority=priority, assignee=assignee,
            sla_status=sla_status, page=1, page_size=10000
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "工单数据"
    headers = ["工单号", "优先级", "状态", "负责人", "SLA状态", "反馈内容", "处理方式", "处理备注", "创建时间", "解决时间"]
    ws.append(headers)
    for tk in items:
        ws.append([
            tk.ticket_id,
            tk.priority,
            tk.status,
            tk.assignee or "",
            tk.sla_status,
            tk.feedback.feedback_text if tk.feedback else "",
            tk.processing_result or "",
            tk.processing_note or "",
            tk.created_at.strftime("%Y-%m-%d %H:%M") if tk.created_at else "",
            tk.resolved_time.strftime("%Y-%m-%d %H:%M") if tk.resolved_time else "",
        ])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=tickets.xlsx"},
    )


@router.get("/tickets/{ticket_id}", response_model=TicketResponse, tags=["ticket"])
async def get_ticket(
    ticket_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("ticket:read")),
):
    ticket = await feedback_service.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/tickets/{ticket_id}", response_model=TicketResponse, tags=["ticket"])
async def update_ticket(
    ticket_id: str,
    data: TicketUpdate,
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("ticket:update")),
):
    try:
        ticket = await feedback_service.update_ticket(db, ticket_id, data, operator=user.username)
        return ticket
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
