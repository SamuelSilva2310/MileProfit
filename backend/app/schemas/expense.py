import datetime

from pydantic import BaseModel


class ExpenseCreate(BaseModel):
    date: datetime.date
    category: str
    subcategory: str | None = None
    description: str | None = None
    amount: float
    station_name: str | None = None
    fuel_type: str | None = None
    price_per_unit: float | None = None
    quantity: float | None = None


class ExpenseUpdate(BaseModel):
    date: datetime.date | None = None
    category: str | None = None
    subcategory: str | None = None
    description: str | None = None
    amount: float | None = None
    station_name: str | None = None
    fuel_type: str | None = None
    price_per_unit: float | None = None
    quantity: float | None = None


class ExpenseResponse(BaseModel):
    id: int
    date: datetime.date
    category: str
    subcategory: str | None
    description: str | None
    amount: float
    station_name: str | None
    fuel_type: str | None
    price_per_unit: float | None
    quantity: float | None

    model_config = {"from_attributes": True}
