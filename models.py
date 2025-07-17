# models.py

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Boolean, DECIMAL, Integer


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100))
    balance: Mapped[float] = mapped_column(DECIMAL(10, 2))
    threshold_limit: Mapped[float] = mapped_column(DECIMAL(10, 2))
    blocking_limit: Mapped[float] = mapped_column(DECIMAL(10, 2))
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
