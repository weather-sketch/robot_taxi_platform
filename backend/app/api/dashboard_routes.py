from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_permission
from app.models.models import UserAccount
from app.schemas.schemas import (
    DashboardOverview,
    DashboardReportRequest,
    DashboardReportResponse,
    DistributionData,
    RouteTrendData,
    TicketMetrics,
    TrendData,
)
from app.services import ai_service, dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/overview", response_model=DashboardOverview)
async def get_overview(
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("dashboard:read")),
):
    return await dashboard_service.get_overview(db)


@router.get("/trends", response_model=TrendData)
async def get_trends(
    days: int = Query(30, ge=1, le=365),
    granularity: str = Query("day", regex="^(day|week|month)$"),
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("dashboard:read")),
):
    return await dashboard_service.get_trends(db, days=days, granularity=granularity)


@router.get("/distribution", response_model=DistributionData)
async def get_distribution(
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("dashboard:read")),
):
    return await dashboard_service.get_distribution(db)


@router.get("/ticket-metrics", response_model=TicketMetrics)
async def get_ticket_metrics(
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("dashboard:read")),
):
    return await dashboard_service.get_ticket_metrics(db)


@router.get("/route-trends", response_model=RouteTrendData)
async def get_route_trends(
    days: int = Query(30, ge=1, le=365),
    top_n: int = Query(8, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("dashboard:read")),
):
    return await dashboard_service.get_route_trends(db, days=days, top_n=top_n)


PERIOD_CONFIG = {
    "daily": {"days": 1, "granularity": "day"},
    "weekly": {"days": 7, "granularity": "day"},
    "monthly": {"days": 30, "granularity": "week"},
}


@router.post("/ai-report", response_model=DashboardReportResponse)
async def generate_ai_report(
    body: DashboardReportRequest,
    db: AsyncSession = Depends(get_db),
    user: UserAccount = Depends(require_permission("ai:analyze")),
):
    cfg = PERIOD_CONFIG[body.period]
    overview = await dashboard_service.get_overview(db)
    trends = await dashboard_service.get_trends(db, days=cfg["days"], granularity=cfg["granularity"])
    distribution = await dashboard_service.get_distribution(db)
    ticket_metrics = await dashboard_service.get_ticket_metrics(db)

    data = {
        "overview": overview.model_dump(),
        "trends": trends.model_dump(),
        "distribution": distribution.model_dump(),
        "ticket_metrics": ticket_metrics.model_dump(),
    }

    try:
        report = await ai_service.generate_dashboard_report(data, body.period)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI report generation failed: {e}")

    return DashboardReportResponse(
        report=report,
        period=body.period,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
