"""Ported from api/Models/Localization/EvalGoldenCase.cs.

Note: no EF migration creates this table yet (see Findings in PORT-MAP.md).
Ported as-is for behavioural fidelity; the schema-parity test lists it as a
known exception.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .eval_case_result import EvalCaseResult
    from .localization_project import LocalizationProject


class EvalGoldenCase(Base):
    __tablename__ = "localization_eval_golden_cases"
    __table_args__ = (
        Index("ix_localization_eval_golden_cases_project_id", "project_id"),
        Index(
            "ix_localization_eval_golden_cases_project_locale",
            "project_id",
            "locale_code",
        ),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("localization_projects.id", ondelete="CASCADE")
    )
    locale_code: Mapped[str] = mapped_column(String(20))
    source_text: Mapped[str] = mapped_column(Text)
    gold_translation: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(30))
    notes: Mapped[str | None] = mapped_column(String(500))

    project: Mapped[LocalizationProject | None] = relationship(
        "LocalizationProject", back_populates="eval_golden_cases", lazy="raise"
    )
    case_results: Mapped[list[EvalCaseResult]] = relationship(
        "EvalCaseResult", back_populates="eval_golden_case", lazy="raise"
    )
