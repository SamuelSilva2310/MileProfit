from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    category: Mapped[str] = mapped_column(String(50))  # fuel_charging, maintenance, improvements, operational
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    amount: Mapped[float] = mapped_column(Float)
    station_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    fuel_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    price_per_unit: Mapped[float | None] = mapped_column(Float, nullable=True)
    quantity: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="expenses")
