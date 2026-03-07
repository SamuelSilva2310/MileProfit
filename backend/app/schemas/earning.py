import datetime

from pydantic import BaseModel


class EarningCreate(BaseModel):
    date: datetime.date
    platform: str
    total_earnings: float
    commission: float = 0.0
    tips: float = 0.0
    bonuses: float = 0.0


class EarningUpdate(BaseModel):
    date: datetime.date | None = None
    platform: str | None = None
    total_earnings: float | None = None
    commission: float | None = None
    tips: float | None = None
    bonuses: float | None = None


class EarningResponse(BaseModel):
    id: int
    date: datetime.date
    platform: str
    total_earnings: float
    commission: float
    tips: float
    bonuses: float

    model_config = {"from_attributes": True}
