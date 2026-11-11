"""Ported from api/Models/MigrationReconciliation.cs."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Index, String
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
            "status IN ('Discovered', 'Mapped', 'Applied', 'Verified', 'Conflict', 'Skipped')",
            name="ck_migration_reconciliation_status",
        ),
    )

    id: Mapped[int] = mapped_column("id", BigInteger, primary_key=True)
    migration_key: Mapped[str] = mapped_column(String(100))
    source_type: Mapped[str] = mapped_column(String(50))
    source_id: Mapped[str] = mapped_column(String(100))
    target_type: Mapped[str | None] = mapped_column(String(50))
    target_id: Mapped[str | None] = mapped_column(String(100))
    source_checksum: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    issue_code: Mapped[str | None] = mapped_column(String(100))
    details_json: Mapped[str] = mapped_column("details", JsonbText)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
