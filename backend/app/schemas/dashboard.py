import datetime

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_earnings: float
    total_expenses: float
    net_profit: float
    total_km: float
    total_hours: float
    activities_count: int
    earnings_per_km: float | None
    earnings_per_hour: float | None
    cost_per_km: float | None
    profit_per_km: float | None
    profit_per_hour: float | None
    estimated_tax: float


class TimeSeriesPoint(BaseModel):
    date: datetime.date
    earnings: float
    expenses: float
    profit: float
    km: float


class PlatformBreakdown(BaseModel):
    platform: str
    total: float


class CategoryBreakdown(BaseModel):
    category: str
    total: float
