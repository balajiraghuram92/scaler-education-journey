"""Ported from api/Models/UserProblemProgress.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .app_user import AppUser
    from .problem import Problem


class UserProblemProgress(Base):
    __tablename__ = "user_problem_progress"
    __table_args__ = (
        Index("IX_user_problem_progress_problem_id", "problem_id"),
        Index(
            "ux_user_problem_progress_user_problem",
            "user_id",
            "problem_id",
            unique=True,
        ),
        CheckConstraint(
            "status::text = ANY (ARRAY['NotStarted'::character varying, 'Attempted'::character varying, 'Solved'::character varying]::text[])",
            name="ck_user_problem_progress_status",
        ),
    )

    id: Mapped[int] = mapped_column("id", BigInteger, Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_users.id", ondelete="CASCADE"))
    problem_id: Mapped[int] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE")
    )
    status: Mapped[str] = mapped_column(String(20), default="Attempted")
    solution_revealed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    solved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    user: Mapped[AppUser | None] = relationship("AppUser", lazy="raise")
    problem: Mapped[Problem | None] = relationship("Problem", lazy="raise")
