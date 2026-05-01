from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.activity import Activity
from app.models.earning import Earning
from app.models.expense import Expense
from app.models.user import User
from app.schemas.dashboard import (
    CategoryBreakdown,
    DashboardSummary,
    PlatformBreakdown,
    TimeSeriesPoint,
)
from app.utils.auth import get_current_user

router = APIRouter()


def _period_range(period: str, ref: date | None = None) -> tuple[date, date]:
    today = ref or date.today()
    if period == "day":
        return today, today
    if period == "week":
        start = today - timedelta(days=today.weekday())
        return start, start + timedelta(days=6)
    if period == "month":
        start = today.replace(day=1)
        next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        end = next_month - timedelta(days=1)
        return start, end
    return today, today


def _resolve_dates(
    period: str, start: date | None, end: date | None
) -> tuple[date, date]:
    if period == "custom" and start and end:
        return start, end
    return _period_range(period)


@router.get("/summary", response_model=DashboardSummary)
async def get_summary(
    period: str = Query("month", pattern="^(day|week|month|custom)$"),
    start: date | None = Query(None),
    end: date | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start_date, end_date = _resolve_dates(period, start, end)

    earnings_result = await db.execute(
        select(
            func.coalesce(func.sum(Earning.total_earnings), 0),
            func.coalesce(func.sum(Earning.tips), 0),
        ).where(
            Earning.user_id == user.id,
            Earning.date >= start_date,
            Earning.date <= end_date,
        )
    )
    row = earnings_result.one()
    total_earnings = float(row[0]) + float(row[1])

    taxable_result = await db.execute(
        select(
            func.coalesce(func.sum(Earning.total_earnings), 0),
            func.coalesce(func.sum(Earning.tips), 0),
        ).where(
            Earning.user_id == user.id,
            Earning.date >= start_date,
            Earning.date <= end_date,
            Earning.is_taxable == True,  # noqa: E712
        )
    )
    tax_row = taxable_result.one()
    taxable_earnings = float(tax_row[0]) + float(tax_row[1])

    expenses_result = await db.execute(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.user_id == user.id,
            Expense.date >= start_date,
            Expense.date <= end_date,
        )
    )
    total_expenses = float(expenses_result.scalar())

    km_result = await db.execute(
        select(
            func.coalesce(func.sum(Activity.end_km - Activity.start_km), 0)
        ).where(
            Activity.user_id == user.id,
            Activity.date >= start_date,
            Activity.date <= end_date,
        )
    )
    total_km = float(km_result.scalar())

    hours_result = await db.execute(
        select(Activity.start_time, Activity.end_time).where(
            Activity.user_id == user.id,
            Activity.date >= start_date,
            Activity.date <= end_date,
            Activity.start_time.is_not(None),
            Activity.end_time.is_not(None),
        )
    )
    total_hours = 0.0
    for s_time, e_time in hours_result.all():
        s_secs = s_time.hour * 3600 + s_time.minute * 60 + s_time.second
        e_secs = e_time.hour * 3600 + e_time.minute * 60 + e_time.second
        if e_secs > s_secs:
            total_hours += (e_secs - s_secs) / 3600

    count_result = await db.execute(
        select(func.count(Earning.id)).where(
            Earning.user_id == user.id,
            Earning.date >= start_date,
            Earning.date <= end_date,
        )
    )
    activities_count = count_result.scalar() or 0

    net_profit = total_earnings - total_expenses
    estimated_tax = taxable_earnings * (user.tax_percent / 100) if user.tax_percent else 0.0

    return DashboardSummary(
        total_earnings=round(total_earnings, 2),
        total_expenses=round(total_expenses, 2),
        net_profit=round(net_profit, 2),
        total_km=round(total_km, 2),
        total_hours=round(total_hours, 2),
        earnings_count=activities_count,
        earnings_per_km=round(total_earnings / total_km, 2) if total_km > 0 else None,
        earnings_per_hour=round(total_earnings / total_hours, 2) if total_hours > 0 else None,
        cost_per_km=round(total_expenses / total_km, 2) if total_km > 0 else None,
        profit_per_km=round(net_profit / total_km, 2) if total_km > 0 else None,
        profit_per_hour=round(net_profit / total_hours, 2) if total_hours > 0 else None,
        estimated_tax=round(estimated_tax, 2),
    )


@router.get("/timeseries", response_model=list[TimeSeriesPoint])
async def get_timeseries(
    period: str = Query("month", pattern="^(day|week|month|custom)$"),
    start: date | None = Query(None),
    end: date | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Daily earnings, expenses, profit, and km for charting."""
    start_date, end_date = _resolve_dates(period, start, end)

    earnings_rows = await db.execute(
        select(
            Earning.date,
            func.sum(Earning.total_earnings + Earning.tips),
        )
        .where(
            Earning.user_id == user.id,
            Earning.date >= start_date,
            Earning.date <= end_date,
        )
        .group_by(Earning.date)
    )
    earnings_by_date = {row[0]: float(row[1]) for row in earnings_rows.all()}

    expenses_rows = await db.execute(
        select(Expense.date, func.sum(Expense.amount))
        .where(
            Expense.user_id == user.id,
            Expense.date >= start_date,
            Expense.date <= end_date,
        )
        .group_by(Expense.date)
    )
    expenses_by_date = {row[0]: float(row[1]) for row in expenses_rows.all()}

    km_rows = await db.execute(
        select(
            Activity.date,
            func.sum(Activity.end_km - Activity.start_km),
        )
        .where(
            Activity.user_id == user.id,
            Activity.date >= start_date,
            Activity.date <= end_date,
        )
        .group_by(Activity.date)
    )
    km_by_date = {row[0]: float(row[1]) for row in km_rows.all()}

    all_dates = sorted(
        set(earnings_by_date) | set(expenses_by_date) | set(km_by_date)
    )

    result = []
    for d in all_dates:
        e = earnings_by_date.get(d, 0.0)
        x = expenses_by_date.get(d, 0.0)
        result.append(
            TimeSeriesPoint(
                date=d,
                earnings=round(e, 2),
                expenses=round(x, 2),
                profit=round(e - x, 2),
                km=round(km_by_date.get(d, 0.0), 2),
            )
        )
    return result


@router.get("/earnings-by-platform", response_model=list[PlatformBreakdown])
async def get_earnings_by_platform(
    period: str = Query("month", pattern="^(day|week|month|custom)$"),
    start: date | None = Query(None),
    end: date | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start_date, end_date = _resolve_dates(period, start, end)
    rows = await db.execute(
        select(
            Earning.platform,
            func.sum(Earning.total_earnings + Earning.tips),
        )
        .where(
            Earning.user_id == user.id,
            Earning.date >= start_date,
            Earning.date <= end_date,
        )
        .group_by(Earning.platform)
        .order_by(func.sum(Earning.total_earnings).desc())
    )
    return [
        PlatformBreakdown(platform=row[0], total=round(float(row[1]), 2))
        for row in rows.all()
    ]


@router.get("/expenses-by-category", response_model=list[CategoryBreakdown])
async def get_expenses_by_category(
    period: str = Query("month", pattern="^(day|week|month|custom)$"),
    start: date | None = Query(None),
    end: date | None = Query(None),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    start_date, end_date = _resolve_dates(period, start, end)
    rows = await db.execute(
        select(Expense.category, func.sum(Expense.amount))
        .where(
            Expense.user_id == user.id,
            Expense.date >= start_date,
            Expense.date <= end_date,
        )
        .group_by(Expense.category)
        .order_by(func.sum(Expense.amount).desc())
    )
    return [
        CategoryBreakdown(category=row[0], total=round(float(row[1]), 2))
        for row in rows.all()
    ]
