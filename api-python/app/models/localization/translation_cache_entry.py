"""Ported from api/Models/Localization/TranslationCacheEntry.cs.

Note: no EF migration creates this table yet (see Findings in PORT-MAP.md).
Ported as-is for behavioural fidelity; the schema-parity test lists it as a
known exception. SourceEmbedding is [NotMapped] in C# and ignored here too.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .localization_project import LocalizationProject


class TranslationCacheEntry(Base):
    __tablename__ = "localization_translation_cache_entries"
    __table_args__ = (
        Index("ix_localization_translation_cache_project_id", "project_id"),
        Index(
            "ix_localization_translation_cache_project_locale",
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
    cached_translation: Mapped[str] = mapped_column(Text)
    hit_count: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_hit_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    project: Mapped[LocalizationProject | None] = relationship(
        "LocalizationProject", back_populates="translation_cache_entries", lazy="raise"
    )
