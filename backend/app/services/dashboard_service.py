from datetime import datetime, timedelta

from sqlalchemy import Integer, case, cast, func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Feedback, SLAStatus, Ticket, TicketStatus
from app.schemas.schemas import (
    DashboardOverview,
    DistributionData,
    DistributionItem,
    RouteTrendData,
    RouteTrendSeries,
    TicketMetrics,
    TrendData,
    TrendPoint,
)


async def get_overview(db: AsyncSession) -> DashboardOverview:
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)

    # Total counts
    total = (await db.execute(select(func.count(Feedback.id)))).scalar() or 0
    total_today = (
        await db.execute(
            select(func.count(Feedback.id)).where(Feedback.feedback_time >= today_start)
        )
    ).scalar() or 0
    total_week = (
        await db.execute(
            select(func.count(Feedback.id)).where(Feedback.feedback_time >= week_start)
        )
    ).scalar() or 0
    total_month = (
        await db.execute(
            select(func.count(Feedback.id)).where(Feedback.feedback_time >= month_start)
        )
    ).scalar() or 0

    # Rating stats
    avg_rating = (
        await db.execute(select(func.avg(Feedback.rating)))
    ).scalar() or 0.0

    # Negative = has a ticket; Positive = no ticket
    negative = (
        await db.execute(
            select(func.count(Feedback.id)).where(Feedback.ticket_id.isnot(None))
        )
    ).scalar() or 0
    positive = total - negative

    positive_rate = (positive / total * 100) if total > 0 else 0.0
    negative_rate = (negative / total * 100) if total > 0 else 0.0

    # Open tickets
    open_tickets = (
        await db.execute(
            select(func.count(Ticket.id)).where(
                Ticket.status.in_([TicketStatus.PENDING.value, TicketStatus.PROCESSING.value])
            )
        )
    ).scalar() or 0

    # SLA compliance (resolved/closed tickets only)
    resolved_total = (
        await db.execute(
            select(func.count(Ticket.id)).where(
                Ticket.status.in_([TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value])
            )
        )
    ).scalar() or 0
    sla_met = (
        await db.execute(
            select(func.count(Ticket.id)).where(
                Ticket.status.in_([TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value]),
                Ticket.sla_status != SLAStatus.OVERDUE.value,
            )
        )
    ).scalar() or 0
    sla_rate = (sla_met / resolved_total * 100) if resolved_total > 0 else 100.0

    return DashboardOverview(
        total_feedbacks=total,
        total_today=total_today,
        total_this_week=total_week,
        total_this_month=total_month,
        avg_rating=round(float(avg_rating), 2),
        positive_rate=round(positive_rate, 1),
        negative_rate=round(negative_rate, 1),
        open_tickets=open_tickets,
        sla_compliance_rate=round(sla_rate, 1),
    )


async def get_trends(
    db: AsyncSession, days: int = 30, granularity: str = "day"
) -> TrendData:
    now = datetime.utcnow()
    start = now - timedelta(days=days)

    # SQLite-compatible date truncation using strftime
    if granularity == "day":
        date_expr = func.strftime("%Y-%m-%d", Feedback.feedback_time)
    elif granularity == "week":
        # SQLite: start of the week (Monday) via strftime with weekday offset
        date_expr = func.strftime(
            "%Y-%m-%d",
            Feedback.feedback_time,
            literal_column("'-' || ((strftime('%w', feedback_time) + 6) % 7) || ' days'"),
        )
    else:
        date_expr = func.strftime("%Y-%m-01", Feedback.feedback_time)

    stmt = (
        select(
            date_expr.label("period"),
            func.count(Feedback.id).label("total"),
            func.sum(case((Feedback.ticket_id.isnot(None), 1), else_=0)).label("negative_count"),
            func.sum(case((Feedback.ticket_id.is_(None), 1), else_=0)).label("positive_count"),
            func.avg(Feedback.rating).label("avg_rating"),
        )
        .where(Feedback.feedback_time >= start)
        .group_by(literal_column("period"))
        .order_by(literal_column("period"))
    )

    result = await db.execute(stmt)
    rows = result.all()

    negative_trend = []
    positive_rate_trend = []
    avg_rating_trend = []

    for row in rows:
        date_str = row.period  # already a string from strftime
        total = row.total or 0
        neg = row.negative_count or 0
        pos = row.positive_count or 0
        avg_r = float(row.avg_rating) if row.avg_rating else 0.0

        negative_trend.append(TrendPoint(date=date_str, value=neg))
        pos_rate = (pos / total * 100) if total > 0 else 0.0
        positive_rate_trend.append(TrendPoint(date=date_str, value=round(pos_rate, 1)))
        avg_rating_trend.append(TrendPoint(date=date_str, value=round(avg_r, 2)))

    return TrendData(
        negative_count=negative_trend,
        positive_rate=positive_rate_trend,
        avg_rating=avg_rating_trend,
    )


async def get_distribution(db: AsyncSession) -> DistributionData:
    total = (await db.execute(select(func.count(Feedback.id)))).scalar() or 1

    # By rating
    rating_stmt = (
        select(Feedback.rating, func.count(Feedback.id).label("cnt"))
        .group_by(Feedback.rating)
        .order_by(Feedback.rating)
    )
    rating_rows = (await db.execute(rating_stmt)).all()
    by_rating = [
        DistributionItem(
            label=f"{r.rating}星", count=r.cnt, percentage=round(r.cnt / total * 100, 1)
        )
        for r in rating_rows
    ]

    # By route (top 10)
    route_stmt = (
        select(Feedback.route, func.count(Feedback.id).label("cnt"))
        .group_by(Feedback.route)
        .order_by(func.count(Feedback.id).desc())
        .limit(10)
    )
    route_rows = (await db.execute(route_stmt)).all()
    by_route = [
        DistributionItem(
            label=r.route, count=r.cnt, percentage=round(r.cnt / total * 100, 1)
        )
        for r in route_rows
    ]

    # By city
    city_stmt = (
        select(Feedback.city, func.count(Feedback.id).label("cnt"))
        .group_by(Feedback.city)
        .order_by(func.count(Feedback.id).desc())
    )
    city_rows = (await db.execute(city_stmt)).all()
    by_city = [
        DistributionItem(
            label=r.city, count=r.cnt, percentage=round(r.cnt / total * 100, 1)
        )
        for r in city_rows
    ]

    # By AI category
    cat_stmt = (
        select(Feedback.ai_category, func.count(Feedback.id).label("cnt"))
        .where(Feedback.ai_category.isnot(None))
        .group_by(Feedback.ai_category)
        .order_by(func.count(Feedback.id).desc())
    )
    cat_rows = (await db.execute(cat_stmt)).all()
    by_category = [
        DistributionItem(
            label=r.ai_category or "未分类",
            count=r.cnt,
            percentage=round(r.cnt / total * 100, 1),
        )
        for r in cat_rows
    ]

    # By time period — SQLite: use strftime('%H', ...) to extract hour as string, cast to int
    hour_expr = cast(func.strftime("%H", Feedback.trip_time), Integer)
    period_case = case(
        (hour_expr.between(7, 9), "早高峰(7-10)"),
        (hour_expr.between(10, 16), "平峰(10-17)"),
        (hour_expr.between(17, 19), "晚高峰(17-20)"),
        else_="其他时段",
    )
    time_stmt = (
        select(period_case.label("period"), func.count(Feedback.id).label("cnt"))
        .group_by(literal_column("period"))
        .order_by(func.count(Feedback.id).desc())
    )
    time_rows = (await db.execute(time_stmt)).all()
    by_time = [
        DistributionItem(
            label=r.period, count=r.cnt, percentage=round(r.cnt / total * 100, 1)
        )
        for r in time_rows
    ]

    return DistributionData(
        by_rating=by_rating,
        by_route=by_route,
        by_city=by_city,
        by_category=by_category,
        by_time_period=by_time,
    )


async def get_ticket_metrics(db: AsyncSession) -> TicketMetrics:
    # By priority
    prio_stmt = (
        select(Ticket.priority, func.count(Ticket.id).label("cnt"))
        .group_by(Ticket.priority)
    )
    prio_rows = (await db.execute(prio_stmt)).all()
    total_tickets = sum(r.cnt for r in prio_rows) or 1
    by_priority = [
        DistributionItem(
            label=r.priority,
            count=r.cnt,
            percentage=round(r.cnt / total_tickets * 100, 1),
        )
        for r in prio_rows
    ]

    # Avg resolve time — computed in Python since SQLite lacks epoch extraction
    resolved_stmt = select(Ticket).where(Ticket.resolved_time.isnot(None))
    resolved_result = await db.execute(resolved_stmt)
    resolved_tickets = list(resolved_result.scalars().all())

    from collections import defaultdict
    resolve_sums: dict[str, list[float]] = defaultdict(list)
    for t in resolved_tickets:
        hours = (t.resolved_time - t.created_at).total_seconds() / 3600
        resolve_sums[t.priority].append(hours)
    avg_resolve = {
        k: round(sum(v) / len(v), 1) for k, v in resolve_sums.items()
    }

    # SLA compliance by priority
    sla_stmt = (
        select(
            Ticket.priority,
            func.count(Ticket.id).label("total"),
            func.sum(case((Ticket.sla_status != SLAStatus.OVERDUE.value, 1), else_=0)).label("met"),
        )
        .where(Ticket.status.in_([TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value]))
        .group_by(Ticket.priority)
    )
    sla_rows = (await db.execute(sla_stmt)).all()
    sla_compliance = {
        r.priority: round(r.met / r.total * 100, 1) if r.total > 0 else 100.0
        for r in sla_rows
    }

    # Open ticket aging
    now = datetime.utcnow()
    open_stmt = select(Ticket).where(
        Ticket.status.in_([TicketStatus.PENDING.value, TicketStatus.PROCESSING.value])
    )
    open_result = await db.execute(open_stmt)
    open_tickets = list(open_result.scalars().all())

    aging_buckets = {"<1天": 0, "1-3天": 0, "3-7天": 0, ">7天": 0}
    for t in open_tickets:
        age = (now - t.created_at).total_seconds() / 86400
        if age < 1:
            aging_buckets["<1天"] += 1
        elif age < 3:
            aging_buckets["1-3天"] += 1
        elif age < 7:
            aging_buckets["3-7天"] += 1
        else:
            aging_buckets[">7天"] += 1

    total_open = len(open_tickets) or 1
    aging = [
        DistributionItem(
            label=k, count=v, percentage=round(v / total_open * 100, 1)
        )
        for k, v in aging_buckets.items()
    ]

    return TicketMetrics(
        by_priority=by_priority,
        avg_resolve_time_hours=avg_resolve,
        sla_compliance_by_priority=sla_compliance,
        open_tickets_aging=aging,
    )


async def get_route_trends(
    db: AsyncSession, days: int = 30, top_n: int = 8
) -> RouteTrendData:
    from collections import defaultdict

    now = datetime.utcnow()
    start = now - timedelta(days=days)

    # Top N routes by feedback count in this period
    top_stmt = (
        select(Feedback.route, func.count(Feedback.id).label("cnt"))
        .where(Feedback.feedback_time >= start)
        .group_by(Feedback.route)
        .order_by(func.count(Feedback.id).desc())
        .limit(top_n)
    )
    top_rows = (await db.execute(top_stmt)).all()
    top_routes = [r.route for r in top_rows]

    if not top_routes:
        return RouteTrendData(dates=[], series=[])

    # Daily counts per route
    date_expr = func.strftime("%Y-%m-%d", Feedback.feedback_time)
    stmt = (
        select(
            date_expr.label("date"),
            Feedback.route,
            func.count(Feedback.id).label("cnt"),
        )
        .where(Feedback.feedback_time >= start, Feedback.route.in_(top_routes))
        .group_by(literal_column("date"), Feedback.route)
        .order_by(literal_column("date"))
    )
    rows = (await db.execute(stmt)).all()

    route_data: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    all_dates: set[str] = set()
    for row in rows:
        all_dates.add(row.date)
        route_data[row.route][row.date] = row.cnt

    dates = sorted(all_dates)
    series = [
        RouteTrendSeries(route=route, data=[route_data[route].get(d, 0) for d in dates])
        for route in top_routes
    ]

    return RouteTrendData(dates=dates, series=series)
