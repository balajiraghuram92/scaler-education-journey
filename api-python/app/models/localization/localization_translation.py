"""Ported from api/Models/Localization/LocalizationTranslation.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    text,
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
        # The migration states these with BETWEEN; PostgreSQL deparses BETWEEN
        # into >= AND <=, so the model carries the deparsed form the database
        # reports (predicted from deparse rules, not observed — the schema
        # parity test confirms).
        CheckConstraint(
            "qps_score IS NULL OR qps_score >= 1 AND qps_score <= 5",
            name="ck_localization_translations_qps_score_range",
        ),
        CheckConstraint(
            "raw_mt_qps_score IS NULL OR raw_mt_qps_score >= 1 AND raw_mt_qps_score <= 5",
            name="ck_localization_translations_raw_mt_qps_score_range",
        ),
    )

    id: Mapped[int] = mapped_column("id", Integer, Identity(), primary_key=True)
    string_id: Mapped[int] = mapped_column(
        ForeignKey("localization_strings.id", ondelete="CASCADE")
    )
    locale_code: Mapped[str] = mapped_column(String(20), default="")
    target_text: Mapped[str | None] = mapped_column(Text)
    stage: Mapped[str] = mapped_column(String(20), default="New")
    translation_source: Mapped[str] = mapped_column(String(20), default="Manual")
    qps_score: Mapped[int | None] = mapped_column(Integer)
    raw_mt_text: Mapped[str | None] = mapped_column(Text)
    raw_mt_qps_score: Mapped[int | None] = mapped_column(Integer)
    comet_kiwi_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    needs_review: Mapped[bool] = mapped_column(
        Boolean, server_default=text("false"), default=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    string: Mapped[LocalizationString | None] = relationship(
        "LocalizationString", back_populates="translations", lazy="raise"
    )
