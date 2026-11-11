"""Ported from api/Models/Localization/LocalizationProject.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .build_snapshot import BuildSnapshot
    from .eval_golden_case import EvalGoldenCase
    from .eval_run import EvalRun
    from .glossary_term import GlossaryTerm
    from .ledger_entry import LedgerEntry
    from .localization_locale import LocalizationLocale
    from .localization_string import LocalizationString
    from .marketplace_job import MarketplaceJob
    from .translation_cache_entry import TranslationCacheEntry
    from .workflow_step import WorkflowStep


class LocalizationProject(Base):
    __tablename__ = "localization_projects"
    __table_args__ = (
        Index("ix_localization_projects_slug", "slug", unique=True),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(150))
    name: Mapped[str] = mapped_column(String(250))
    source_locale: Mapped[str] = mapped_column(String(20))
    qps_threshold: Mapped[int] = mapped_column(Integer, server_default=text("70"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    locales: Mapped[list[LocalizationLocale]] = relationship(
        "LocalizationLocale", back_populates="project", lazy="raise"
    )
    strings: Mapped[list[LocalizationString]] = relationship(
        "LocalizationString", back_populates="project", lazy="raise"
    )
    workflow_steps: Mapped[list[WorkflowStep]] = relationship(
        "WorkflowStep", back_populates="project", lazy="raise"
    )
    build_snapshots: Mapped[list[BuildSnapshot]] = relationship(
        "BuildSnapshot", back_populates="project", lazy="raise"
    )
    marketplace_jobs: Mapped[list[MarketplaceJob]] = relationship(
        "MarketplaceJob", back_populates="project", lazy="raise"
    )
    ledger_entries: Mapped[list[LedgerEntry]] = relationship(
        "LedgerEntry", back_populates="project", lazy="raise"
    )
    glossary_terms: Mapped[list[GlossaryTerm]] = relationship(
        "GlossaryTerm", back_populates="project", lazy="raise"
    )
    translation_cache_entries: Mapped[list[TranslationCacheEntry]] = relationship(
        "TranslationCacheEntry", back_populates="project", lazy="raise"
    )
    eval_golden_cases: Mapped[list[EvalGoldenCase]] = relationship(
        "EvalGoldenCase", back_populates="project", lazy="raise"
    )
    eval_runs: Mapped[list[EvalRun]] = relationship(
        "EvalRun", back_populates="project", lazy="raise"
    )
