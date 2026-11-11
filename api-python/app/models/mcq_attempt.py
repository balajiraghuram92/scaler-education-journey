"""Ported from api/Models/McqAttempt.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .mcq_presentation import McqPresentation


class McqAttempt(Base):
    __tablename__ = "mcq_attempts"
    __table_args__ = (
        Index("ux_mcq_attempts_presentation_id", "presentation_id", unique=True),
    )

    id: Mapped[UUID] = mapped_column("id", Uuid, primary_key=True, default=uuid4)
    presentation_id: Mapped[UUID] = mapped_column(
        ForeignKey("mcq_presentations.id", ondelete="CASCADE")
    )
    selected_option_key: Mapped[str] = mapped_column(String(10), default="")
    is_correct: Mapped[bool] = mapped_column(Boolean)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    presentation: Mapped[McqPresentation | None] = relationship(
        "McqPresentation", back_populates="attempt", lazy="raise"
    )
