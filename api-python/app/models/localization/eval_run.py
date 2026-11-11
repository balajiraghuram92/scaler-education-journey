"""Ported from api/Models/Localization/EvalRun.cs.

Note: no EF migration creates this table yet (see Findings in PORT-MAP.md).
Ported as-is for behavioural fidelity; the schema-parity test lists it as a
known exception.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .eval_case_result import EvalCaseResult
    from .localization_project import LocalizationProject


class EvalRun(Base):
    __tablename__ = "localization_eval_runs"
    __table_args__ = (
        Index("ix_localization_eval_runs_project_id", "project_id"),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("localization_projects.id", ondelete="CASCADE")
    )
    pipeline_config: Mapped[str] = mapped_column(String(50))
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    avg_comet_kiwi: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    avg_qps_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    glossary_adherence_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    placeholder_preservation_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    cache_hit_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    avg_latency_ms: Mapped[int | None] = mapped_column(Integer)
    total_cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))

    project: Mapped[LocalizationProject | None] = relationship(
        "LocalizationProject", back_populates="eval_runs", lazy="raise"
    )
    case_results: Mapped[list[EvalCaseResult]] = relationship(
        "EvalCaseResult", back_populates="eval_run", lazy="raise"
    )
