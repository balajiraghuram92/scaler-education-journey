"""Ported from api/Models/MfaChallenge.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .app_user import AppUser


class MfaChallenge(Base):
    __tablename__ = "mfa_challenges"
    __table_args__ = (
        Index("ix_mfa_challenges_user_id", "user_id"),
        Index("ix_mfa_challenges_expires_at", "expires_at"),
        CheckConstraint(
            "purpose IN ('Enrollment', 'Login')", name="ck_mfa_challenges_purpose"
        ),
    )

    id: Mapped[UUID] = mapped_column("id", Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_users.id", ondelete="CASCADE"))
    purpose: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    failed_attempts: Mapped[int] = mapped_column(Integer)

    user: Mapped[AppUser | None] = relationship("AppUser", lazy="raise")
