"""Ported from api/Models/Localization/EvalCaseResult.cs.

Note: no EF migration creates this table yet (see Findings in PORT-MAP.md).
Ported as-is for behavioural fidelity; the schema-parity test lists it as a
known exception.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Identity, Index, Integer, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .eval_golden_case import EvalGoldenCase
    from .eval_run import EvalRun


class EvalCaseResult(Base):
    __tablename__ = "localization_eval_case_results"
    __table_args__ = (
        Index("ix_localization_eval_case_results_run_id", "eval_run_id"),
        Index("ix_localization_eval_case_results_case_id", "eval_golden_case_id"),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    eval_run_id: Mapped[int] = mapped_column(
        ForeignKey("localization_eval_runs.id", ondelete="CASCADE")
    )
    eval_golden_case_id: Mapped[int] = mapped_column(
        ForeignKey("localization_eval_golden_cases.id", ondelete="CASCADE")
    )
    produced_translation: Mapped[str] = mapped_column(Text, default="")
    comet_kiwi_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    qps_score: Mapped[int | None] = mapped_column(Integer)
    glossary_adherence_ok: Mapped[bool | None] = mapped_column(Boolean)
    placeholder_preserved_ok: Mapped[bool | None] = mapped_column(Boolean)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    cache_hit: Mapped[bool | None] = mapped_column(Boolean)
    cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(12, 6))

    eval_run: Mapped[EvalRun | None] = relationship(
        "EvalRun", back_populates="case_results", lazy="raise"
    )
    eval_golden_case: Mapped[EvalGoldenCase | None] = relationship(
        "EvalGoldenCase", back_populates="case_results", lazy="raise"
    )
