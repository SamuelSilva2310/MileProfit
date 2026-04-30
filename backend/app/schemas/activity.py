import datetime

from pydantic import BaseModel


class ActivityCreate(BaseModel):
    date: datetime.date
    start_km: float
    end_km: float
    start_time: datetime.time | None = None
    end_time: datetime.time | None = None
    vehicle_id: int | None = None


class ActivityUpdate(BaseModel):
    date: datetime.date | None = None
    start_km: float | None = None
    end_km: float | None = None
    start_time: datetime.time | None = None
    end_time: datetime.time | None = None
    vehicle_id: int | None = None


class ActivityResponse(BaseModel):
    id: int
    date: datetime.date
    start_km: float
    end_km: float
    total_km: float
    start_time: datetime.time | None
    end_time: datetime.time | None
    vehicle_id: int | None

    model_config = {"from_attributes": True}
