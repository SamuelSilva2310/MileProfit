from pydantic import field_validator
from pydantic_settings import BaseSettings

_INSECURE_DEFAULTS = {
    "change-me-in-production-use-a-real-secret",
    "change-me-generate-with-openssl-rand-hex-32",
}


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./rider_expenses.db"
    SECRET_KEY: str = "change-me-in-production-use-a-real-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    # Login rate limit (requests per minute per IP)
    LOGIN_RATE_LIMIT: str = "10/minute"

    # Sentry — leave empty to disable
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "production"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_must_be_set(cls, v: str) -> str:
        if v in _INSECURE_DEFAULTS or len(v) < 32:
            raise ValueError(
                "SECRET_KEY is insecure. Generate one with: openssl rand -hex 32"
            )
        return v


settings = Settings()
