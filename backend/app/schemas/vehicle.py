from pydantic import BaseModel


class VehicleCreate(BaseModel):
    name: str
    is_primary: bool = False


class VehicleUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None
    is_primary: bool | None = None


class VehicleResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    is_primary: bool

    model_config = {"from_attributes": True}
