"""Ported from api/Models/AppUser.cs."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class AppUser(Base):
    __tablename__ = "app_users"
    __table_args__ = (
        Index("ix_app_users_email", "email", unique=True),
        Index("IX_app_users_decided_by_user_id", "decided_by_user_id"),
        CheckConstraint(
            "role::text = ANY (ARRAY['User'::character varying, 'Admin'::character varying]::text[])",
            name="ck_app_users_role",
        ),
        CheckConstraint(
            "status::text = ANY (ARRAY['PendingApproval'::character varying, 'Approved'::character varying, 'Rejected'::character varying, 'Disabled'::character varying]::text[])",
            name="ck_app_users_status",
        ),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), default="")
    password_hash: Mapped[str] = mapped_column(Text, default="")
    password_salt: Mapped[str] = mapped_column(Text, default="")
    password_iterations: Mapped[int] = mapped_column(
        Integer, server_default=text("100000"), default=210000
    )
    role: Mapped[str] = mapped_column(String(20), server_default=text("'User'"), default="User")
    status: Mapped[str] = mapped_column(
        String(30), server_default=text("'PendingApproval'"), default="PendingApproval"
    )
    display_name: Mapped[str | None] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        default=lambda: datetime.now(UTC),
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decided_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("app_users.id", ondelete="RESTRICT")
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    totp_secret_encrypted: Mapped[str | None] = mapped_column(Text)
    totp_enabled: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), default=False
    )
    last_accepted_totp_counter: Mapped[int | None] = mapped_column(BigInteger)

    decided_by_user: Mapped[AppUser | None] = relationship(
        "AppUser", remote_side="AppUser.id", lazy="raise"
    )
