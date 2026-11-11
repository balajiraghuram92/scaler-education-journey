"""Ported from api/Models/MigrationReconciliation.cs."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Identity, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .types import JsonbText


class MigrationReconciliation(Base):
    __tablename__ = "migration_reconciliation"
    __table_args__ = (
        Index("ix_migration_reconciliation_status", "migration_key", "status"),
        Index(
            "ux_migration_reconciliation_identity",
            "migration_key",
            "source_type",
            "source_id",
            unique=True,
        ),
        CheckConstraint(
            "status::text = ANY (ARRAY['Discovered'::character varying, 'Mapped'::character varying, 'Applied'::character varying, 'Verified'::character varying, 'Conflict'::character varying, 'Skipped'::character varying]::text[])",
            name="ck_migration_reconciliation_status",
        ),
    )

    id: Mapped[int] = mapped_column("id", BigInteger, Identity(), primary_key=True)
    migration_key: Mapped[str] = mapped_column(String(100), default="")
    source_type: Mapped[str] = mapped_column(String(50), default="")
    source_id: Mapped[str] = mapped_column(String(100), default="")
    target_type: Mapped[str | None] = mapped_column(String(50), default="")
    target_id: Mapped[str | None] = mapped_column(String(100), default="")
    source_checksum: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(32), default="Discovered")
    issue_code: Mapped[str | None] = mapped_column(String(100), default="")
    details_json: Mapped[str] = mapped_column(
        "details", JsonbText, server_default=text("'{}'::jsonb"), default="{}"
    )
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
        default=lambda: datetime.now(UTC),
    )
