"""Ported from api/Models/Localization/LocalizationTranslation.cs.

Note: the C# class declares raw_mt_text, raw_mt_qps_score and
comet_kiwi_score, but the latest EF migration does not create those columns
(see Findings in PORT-MAP.md). They are ported as-is for behavioural
fidelity; the schema-parity test lists them as known exceptions.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .localization_string import LocalizationString


class LocalizationTranslation(Base):
    __tablename__ = "localization_translations"
    __table_args__ = (
        Index(
            "ix_localization_translations_string_id_locale_code",
            "string_id",
            "locale_code",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column("id", Integer, primary_key=True)
    string_id: Mapped[int] = mapped_column(
        ForeignKey("localization_strings.id", ondelete="CASCADE")
    )
    locale_code: Mapped[str] = mapped_column(String(20))
    target_text: Mapped[str | None] = mapped_column(Text)
    stage: Mapped[str] = mapped_column(String(20))
    translation_source: Mapped[str] = mapped_column(String(20))
    qps_score: Mapped[int | None] = mapped_column(Integer)
    raw_mt_text: Mapped[str | None] = mapped_column(Text)
    raw_mt_qps_score: Mapped[int | None] = mapped_column(Integer)
    comet_kiwi_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    needs_review: Mapped[bool] = mapped_column(Boolean)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    string: Mapped[LocalizationString | None] = relationship(
        "LocalizationString", back_populates="translations", lazy="raise"
    )
