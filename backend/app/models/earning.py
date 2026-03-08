from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Earning(Base):
    __tablename__ = "earnings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    platform: Mapped[str] = mapped_column(String(100))
    total_earnings: Mapped[float] = mapped_column(Float)
    tips: Mapped[float] = mapped_column(Float, default=0.0)
    is_taxable: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="earnings")
