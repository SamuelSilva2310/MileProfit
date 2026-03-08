import datetime

from pydantic import BaseModel


class EarningCreate(BaseModel):
    date: datetime.date
    platform: str
    total_earnings: float
    tips: float = 0.0
    is_taxable: bool = True


class EarningUpdate(BaseModel):
    date: datetime.date | None = None
    platform: str | None = None
    total_earnings: float | None = None
    tips: float | None = None
    is_taxable: bool | None = None


class EarningResponse(BaseModel):
    id: int
    date: datetime.date
    platform: str
    total_earnings: float
    tips: float
    is_taxable: bool

    model_config = {"from_attributes": True}
