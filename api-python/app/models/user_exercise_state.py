"""Ported from api/Models/UserExerciseState.cs.

Holds both classes from the C# file: UserExerciseDraft and UserExerciseAttempt.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .types import JsonbText

if TYPE_CHECKING:
    from .app_user import AppUser


class UserExerciseDraft(Base):
    __tablename__ = "user_exercise_drafts"
    __table_args__ = (
        Index(
            "ux_user_exercise_drafts_user_exercise",
            "user_id",
            "exercise_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_users.id", ondelete="CASCADE"))
    exercise_id: Mapped[str] = mapped_column(String(120))
    files_json: Mapped[str] = mapped_column("files", JsonbText)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped[AppUser | None] = relationship("AppUser", lazy="raise")


class UserExerciseAttempt(Base):
    __tablename__ = "user_exercise_attempts"
    __table_args__ = (
        Index(
            "ix_user_exercise_attempts_user_exercise_time",
            "user_id",
            "exercise_id",
            "submitted_at",
        ),
        CheckConstraint(
            "status IN ('success', 'testFailure', 'compilationFailure', 'timeout')",
            name="ck_user_exercise_attempts_status",
        ),
    )

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_users.id", ondelete="CASCADE"))
    exercise_id: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(30))
    tests_total: Mapped[int] = mapped_column(Integer)
    tests_passed: Mapped[int] = mapped_column(Integer)
    duration_milliseconds: Mapped[int] = mapped_column("duration_ms", BigInteger)
    files_json: Mapped[str] = mapped_column("files", JsonbText)
    summary_json: Mapped[str] = mapped_column("summary", JsonbText)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped[AppUser | None] = relationship("AppUser", lazy="raise")
