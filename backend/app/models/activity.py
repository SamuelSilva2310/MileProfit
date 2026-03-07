from datetime import date, datetime, time

from sqlalchemy import Date, DateTime, Float, ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    start_km: Mapped[float] = mapped_column(Float)
    end_km: Mapped[float] = mapped_column(Float)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activities")

    @property
    def total_km(self) -> float:
        return self.end_km - self.start_km
