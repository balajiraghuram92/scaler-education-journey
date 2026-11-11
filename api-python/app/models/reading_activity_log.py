"""Ported from api/Models/ReadingActivityLog.cs."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ReadingActivityLog(Base):
    __tablename__ = "reading_activity_logs"
    __table_args__ = (Index("IX_reading_activity_logs_DayLabel", "DayLabel"),)

    id: Mapped[int] = mapped_column("Id", Integer, primary_key=True)
    day_label: Mapped[str] = mapped_column("DayLabel", Text)
    activity_count: Mapped[int] = mapped_column("ActivityCount", Integer)
    order_index: Mapped[int] = mapped_column("OrderIndex", Integer)
    log_date: Mapped[datetime] = mapped_column("LogDate", DateTime(timezone=True))
