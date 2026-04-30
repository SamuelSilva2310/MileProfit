from pydantic import BaseModel, EmailStr, field_validator


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name is required")
        return v.strip()


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
