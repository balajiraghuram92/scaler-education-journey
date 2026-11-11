"""Ported from api/Models/Localization/WorkflowStep.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .localization_project import LocalizationProject


class WorkflowStep(Base):
    __tablename__ = "localization_workflow_steps"
    __table_args__ = (
        Index("ix_localization_workflow_steps_project_id", "project_id"),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("localization_projects.id", ondelete="CASCADE")
    )
    order: Mapped[int] = mapped_column("order", Integer)
    trigger: Mapped[str] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(50))
    condition_expression: Mapped[str | None] = mapped_column(String(200))
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_run_outcome: Mapped[str | None] = mapped_column(String(200))

    project: Mapped[LocalizationProject | None] = relationship(
        "LocalizationProject", back_populates="workflow_steps", lazy="raise"
    )
