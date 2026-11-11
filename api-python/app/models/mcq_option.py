"""Ported from api/Models/McqOption.cs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Identity, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .mcq_question import McqQuestion


class McqOption(Base):
    __tablename__ = "mcq_options"
    __table_args__ = (Index("ix_mcq_options_question_id", "question_id"),)

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("mcq_questions.id", ondelete="CASCADE")
    )
    option_key: Mapped[str] = mapped_column(String(10), default="")
    option_text: Mapped[str] = mapped_column(Text, default="")
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)

    question: Mapped[McqQuestion | None] = relationship(
        "McqQuestion", back_populates="options", lazy="raise"
    )
