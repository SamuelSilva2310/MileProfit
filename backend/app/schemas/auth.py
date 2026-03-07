from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    vehicle_name: str | None
    tax_percent: float
    is_admin: bool

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: str | None = None
    vehicle_name: str | None = None
    tax_percent: float | None = None
