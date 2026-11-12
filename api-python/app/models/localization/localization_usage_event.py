"""Ported from api/Models/Localization/LocalizationUsageEvent.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .localization_project import LocalizationProject
    from .workflow_step import WorkflowStep


class LocalizationUsageEvent(Base):
    __tablename__ = "localization_usage_events"
    __table_args__ = (
        Index("ix_localization_usage_events_project_occurred", "project_id", "occurred_at"),
        Index("ix_localization_usage_events_meter_occurred", "meter", "occurred_at"),
        Index("ix_localization_usage_events_workflow_step_id", "workflow_step_id"),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("localization_projects.id", ondelete="CASCADE")
    )
    workflow_step_id: Mapped[int | None] = mapped_column(
        ForeignKey("localization_workflow_steps.id", ondelete="SET NULL")
    )
    meter: Mapped[str] = mapped_column(String(30), default="")
    operation: Mapped[str] = mapped_column(String(30), default="")
    locale_code: Mapped[str | None] = mapped_column(String(20))
    units: Mapped[int] = mapped_column(Integer)
    units_out: Mapped[int | None] = mapped_column(Integer)
    cache_hit: Mapped[bool] = mapped_column(Boolean)
    succeeded: Mapped[bool] = mapped_column(Boolean)
    cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    # One-sided like the C# WithMany(): no collection on project or step.
    project: Mapped[LocalizationProject | None] = relationship(
        "LocalizationProject", lazy="raise"
    )
    workflow_step: Mapped[WorkflowStep | None] = relationship(
        "WorkflowStep", lazy="raise"
    )
