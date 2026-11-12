"""Ported from api/Models/Localization/LocalizationProject.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Identity, Index, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .build_snapshot import BuildSnapshot
    from .eval_golden_case import EvalGoldenCase
    from .eval_run import EvalRun
    from .glossary_term import GlossaryTerm
    from .localization_locale import LocalizationLocale
    from .localization_string import LocalizationString
    from .translation_cache_entry import TranslationCacheEntry
    from .translation_job import TranslationJob
    from .workflow_step import WorkflowStep


class LocalizationProject(Base):
    __tablename__ = "localization_projects"
    __table_args__ = (
        Index("ix_localization_projects_slug", "slug", unique=True),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    slug: Mapped[str] = mapped_column(String(150), default="")
    name: Mapped[str] = mapped_column(String(250), default="")
    source_locale: Mapped[str] = mapped_column(String(20), default="en-US")
    qps_threshold: Mapped[int] = mapped_column(Integer, server_default=text("4"), default=4)
    client_alias: Mapped[str] = mapped_column(String(100), default="")
    # The R2 migration gives ai_enabled a database default (TRUE) that the EF
    # model does not declare (no HasDefaultValue in the snapshot): server
    # default follows the migration, the Python default follows the C#
    # initializer, and both coexist.
    ai_enabled: Mapped[bool] = mapped_column(
        Boolean, server_default=text("true"), default=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

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
    translation_jobs: Mapped[list[TranslationJob]] = relationship(
        "TranslationJob", back_populates="project", lazy="raise"
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
