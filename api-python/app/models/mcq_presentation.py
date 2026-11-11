"""Ported from api/Models/McqPresentation.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .types import JsonbText

if TYPE_CHECKING:
    from .app_user import AppUser
    from .mcq_attempt import McqAttempt
    from .mcq_question import McqQuestion


class McqPresentation(Base):
    __tablename__ = "mcq_presentations"
    __table_args__ = (
        Index("ix_mcq_presentations_user_id", "user_id"),
        Index("ix_mcq_presentations_question_id", "question_id"),
    )

    id: Mapped[UUID] = mapped_column("id", Uuid, primary_key=True, default=uuid4)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("mcq_questions.id", ondelete="CASCADE")
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("app_users.id", ondelete="SET NULL")
    )
    displayed_option_order: Mapped[str] = mapped_column(
        "displayed_option_order", JsonbText
    )
    question_text_shown: Mapped[str | None] = mapped_column(Text)
    presented_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    question: Mapped[McqQuestion | None] = relationship(
        "McqQuestion", back_populates="presentations", lazy="raise"
    )
    user: Mapped[AppUser | None] = relationship("AppUser", lazy="raise")
    attempt: Mapped[McqAttempt | None] = relationship(
        "McqAttempt", back_populates="presentation", uselist=False, lazy="raise"
    )
