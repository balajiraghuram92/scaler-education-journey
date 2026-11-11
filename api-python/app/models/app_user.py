"""Ported from api/Models/AppUser.cs."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AppUser(Base):
    __tablename__ = "app_users"
    __table_args__ = (
        Index("ix_app_users_email", "email", unique=True),
        Index("IX_app_users_DecidedByUserId", "decided_by_user_id"),
        CheckConstraint("role IN ('User', 'Admin')", name="ck_app_users_role"),
        CheckConstraint(
            "status IN ('PendingApproval', 'Approved', 'Rejected', 'Disabled')",
            name="ck_app_users_status",
        ),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(320))
    password_hash: Mapped[str] = mapped_column(Text)
    password_salt: Mapped[str] = mapped_column(Text)
    password_iterations: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(30))
    display_name: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decided_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("app_users.id", ondelete="RESTRICT")
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    totp_secret_encrypted: Mapped[str | None] = mapped_column(Text)
    totp_enabled: Mapped[bool] = mapped_column(Boolean)
    last_accepted_totp_counter: Mapped[int | None] = mapped_column(BigInteger)

    decided_by_user: Mapped[AppUser | None] = relationship(
        "AppUser", remote_side="AppUser.id", lazy="raise"
    )
