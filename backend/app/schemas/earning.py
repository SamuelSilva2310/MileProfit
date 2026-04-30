import datetime

from pydantic import BaseModel


class EarningCreate(BaseModel):
    date: datetime.date
    platform: str
    total_earnings: float
    tips: float = 0.0
    is_taxable: bool = True
    notes: str | None = None
    is_paid: bool = True
    vehicle_id: int | None = None


class EarningUpdate(BaseModel):
    date: datetime.date | None = None
    platform: str | None = None
    total_earnings: float | None = None
    tips: float | None = None
    is_taxable: bool | None = None
    notes: str | None = None
    is_paid: bool | None = None
    vehicle_id: int | None = None


class EarningResponse(BaseModel):
    id: int
    date: datetime.date
    platform: str
    total_earnings: float
    tips: float
    is_taxable: bool
    notes: str | None
    is_paid: bool
    vehicle_id: int | None

    model_config = {"from_attributes": True}
