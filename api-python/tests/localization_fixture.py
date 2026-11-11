"""Translated from LocalizationTestFixture.cs: fakes and seed helpers.

Not a test module (no test_* functions); imported by the localization
service/workflow test modules. Uses the shared scratch_session fixture from
conftest.py (rolled back after every test).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.localization.localization_locale import LocalizationLocale
from app.models.localization.localization_project import LocalizationProject
from app.models.localization.localization_string import LocalizationString
from app.models.localization.vendor import Vendor
from app.services.localization.auto_routing_service import AutoRoutingService
from app.services.localization.credit_ledger_service import CreditLedgerService
from app.services.localization.i_quality_scorer import QualityScoreResult
from app.services.localization.marketplace_service import MarketplaceService
from app.services.localization.mt_optimize_service import MtOptimizeService
from app.services.localization.vendor_portal_service import VendorPortalService
from app.services.localization.workflow_service import WorkflowService


class FakeTranslationProvider:
    async def translate_async(
        self, source_text: str, source_locale: str, target_locale: str
    ) -> str:
        return f"[{target_locale}]{source_text}"


class FakeQualityScorer:
    async def score_async(
        self, source_text: str, target_text: str, target_locale: str
    ) -> QualityScoreResult:
        return QualityScoreResult(90, [])


@dataclass
class SeededProject:
    project: LocalizationProject
    strings: list[LocalizationString]
    vendor: Vendor


async def seed_project(
    db: AsyncSession,
    slug: str = "test-proj",
    vendor_languages: str = "de-DE,fr-FR",
) -> SeededProject:
    now = datetime.now(UTC)
    project = LocalizationProject(
        slug=slug,
        name="Test Project",
        source_locale="en-US",
        qps_threshold=70,
        created_at=now,
    )
    db.add(project)
    await db.flush()
    db.add_all(
        [
            LocalizationLocale(
                project_id=project.id, locale_code="de-DE", display_name="German"
            ),
            LocalizationLocale(
                project_id=project.id, locale_code="fr-FR", display_name="French"
            ),
        ]
    )
    s1 = LocalizationString(
        project_id=project.id,
        key="k.one",
        source_text="Hello world",
        created_at=now,
    )
    s2 = LocalizationString(
        project_id=project.id,
        key="k.two",
        source_text="Goodbye moon",
        created_at=now,
    )
    db.add_all([s1, s2])
    vendor = Vendor(
        name="Test Vendor", languages=vendor_languages, rating=Decimal("4.5")
    )
    db.add(vendor)
    await db.flush()
    return SeededProject(project, [s1, s2], vendor)


def marketplace(db: AsyncSession) -> MarketplaceService:
    return MarketplaceService(db, CreditLedgerService(db))


def vendor_portal(db: AsyncSession) -> VendorPortalService:
    return VendorPortalService(db, marketplace(db))


def workflow(db: AsyncSession) -> WorkflowService:
    return WorkflowService(
        db,
        FakeTranslationProvider(),
        MtOptimizeService(),
        FakeQualityScorer(),
        AutoRoutingService(),
        marketplace(db),
    )
