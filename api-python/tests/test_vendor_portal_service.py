"""Translated from VendorPortalServiceTests.cs."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.localization.localization_translation import LocalizationTranslation
from app.models.localization.translation_job import TranslationJob
from app.models.localization.vendor import Vendor
from app.schemas.localization_dtos import AddWorkflowStepRequest
from app.services.localization.auto_routing_service import AutoRoutingService
from app.services.localization.localization_ai_client import LocalizationAiClient
from app.services.localization.localization_exceptions import InvalidJobStateException
from app.services.localization.mt_optimize_service import MtOptimizeService
from app.services.localization.workflow_service import WorkflowService
from app.settings import LocalizationAiSettings

from .localization_fixture import (
    FakeQualityScorer,
    FakeTranslationProvider,
    jobs,
    seed_project,
    vendor_portal,
)


async def _seed_vendor(
    db: AsyncSession,
    alias: str = "Vendor Team Test",
    name: str = "Test Team",
) -> Vendor:
    vendor = Vendor(name=name, alias=alias, languages="de-DE,fr-FR")
    db.add(vendor)
    await db.flush()
    return vendor


async def _seed_job(
    db: AsyncSession,
    project_id: int,
    vendor_id: int,
    status: str,
    locale_code: str = "de-DE",
) -> TranslationJob:
    job = TranslationJob(
        project_id=project_id,
        locale_code=locale_code,
        status=status,
        string_count=2,
        word_count=4,
        vendor_id=vendor_id,
        created_at=datetime.now(UTC),
    )
    db.add(job)
    await db.flush()
    return job


class _CountingOptimizeHandler:
    """File-local counting fake for the optimize endpoint: the queued fakes
    live in other test modules, so this test carries its own handler."""

    def __init__(self) -> None:
        self.call_count = 0

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.call_count += 1
        return httpx.Response(
            200,
            text='{"optimizedTranslation":"opt","cacheHit":false,"checks":{},'
            '"inputTokens":10,"outputTokens":5,"tokensUsed":15,"latencyMs":3,'
            '"fallback":false}',
        )


def _optimize_client(handler: _CountingOptimizeHandler) -> LocalizationAiClient:
    options = LocalizationAiSettings(
        **{"LocalizationAi__BaseUrl": "http://ai/"}
    )
    http_client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler.handler), base_url="http://ai/"
    )
    return LocalizationAiClient(options=options, http_client=http_client)


@pytest.mark.asyncio
async def test_get_vendor_roster_returns_aliases_without_real_names(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    await _seed_vendor(db, "Vendor Team Larch", "Maria Fischer")
    await _seed_vendor(db, "Vendor Team Osprey", "Kenji Sato")
    portal = vendor_portal(db)

    roster = await portal.get_vendor_roster_async()

    assert len(roster) == 2
    assert roster[0].alias == "Vendor Team Larch"
    assert roster[0].languages == "de-DE,fr-FR"
    assert roster[1].alias == "Vendor Team Osprey"


@pytest.mark.asyncio
async def test_get_jobs_for_vendor_returns_own_jobs_newest_first(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    seed.project.client_alias = "Client Team Kestrel"
    await db.flush()
    mine = await _seed_vendor(db, "Vendor Team Mine")
    other = await _seed_vendor(db, "Vendor Team Other", "Other Team")
    old_job = await _seed_job(db, seed.project.id, mine.id, "Approved")
    old_job.created_at = datetime.now(UTC) - timedelta(days=2)
    new_job = await _seed_job(db, seed.project.id, mine.id, "Assigned")
    await _seed_job(db, seed.project.id, other.id, "Assigned")
    await db.flush()
    portal = vendor_portal(db)

    found = await portal.get_jobs_for_vendor_async(mine.id)

    assert len(found) == 2
    assert found[0].id == new_job.id
    assert found[1].id == old_job.id
    assert all(j.client_alias == "Client Team Kestrel" for j in found)


@pytest.mark.asyncio
async def test_update_job_string_on_assigned_job_saves_target_and_returns_vendor_row(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    job = await _seed_job(db, seed.project.id, vendor.id, "Assigned")
    portal = vendor_portal(db)

    row = await portal.update_job_string_async(
        job.id, seed.strings[0].id, "Hallo Welt"
    )

    assert row.target_text == "Hallo Welt"
    assert row.stage == "Translated"
    assert row.score is None
    assert row.needs_review is False

    reloaded = (
        await db.execute(
            select(TranslationJob).where(TranslationJob.id == job.id)
        )
    ).scalar_one()
    assert reloaded.status == "InProgress"


@pytest.mark.asyncio
async def test_update_job_string_on_approved_job_is_rejected(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    job = await _seed_job(db, seed.project.id, vendor.id, "Approved")
    portal = vendor_portal(db)

    with pytest.raises(InvalidJobStateException):
        await portal.update_job_string_async(job.id, seed.strings[0].id, "x")


@pytest.mark.asyncio
async def test_update_job_string_on_needs_revision_moves_job_to_in_progress(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    job = await _seed_job(db, seed.project.id, vendor.id, "NeedsRevision")
    portal = vendor_portal(db)

    await portal.update_job_string_async(job.id, seed.strings[0].id, "Hallo Welt")

    reloaded = (
        await db.execute(
            select(TranslationJob).where(TranslationJob.id == job.id)
        )
    ).scalar_one()
    assert reloaded.status == "InProgress"


@pytest.mark.asyncio
async def test_update_job_string_on_submitted_for_review_is_rejected(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    job = await _seed_job(db, seed.project.id, vendor.id, "SubmittedForReview")
    portal = vendor_portal(db)

    with pytest.raises(InvalidJobStateException):
        await portal.update_job_string_async(job.id, seed.strings[0].id, "x")


@pytest.mark.asyncio
async def test_submit_job_for_review_transitions_to_submitted_for_review(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    seed.project.client_alias = "Client Team Kestrel"
    await db.flush()
    vendor = await _seed_vendor(db)
    job = await _seed_job(db, seed.project.id, vendor.id, "InProgress")
    now = datetime.now(UTC)
    for item in seed.strings:
        db.add(
            LocalizationTranslation(
                string_id=item.id,
                locale_code="de-DE",
                target_text="done",
                stage="Translated",
                translation_source="Marketplace",
                needs_review=False,
                updated_at=now,
            )
        )
    await db.flush()
    portal = vendor_portal(db)

    row = await portal.submit_job_for_review_async(job.id)

    assert row.status == "SubmittedForReview"
    assert row.client_alias == "Client Team Kestrel"
    assert row.submitted_at is not None


@pytest.mark.asyncio
async def test_update_job_string_same_text_accepts_machine_draft(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    job = await _seed_job(db, seed.project.id, vendor.id, "Assigned")
    db.add(
        LocalizationTranslation(
            string_id=seed.strings[0].id,
            locale_code="de-DE",
            target_text="maschinell",
            raw_mt_text="maschinell",
            stage="Translated",
            translation_source="AI",
            needs_review=False,
            updated_at=datetime.now(UTC),
        )
    )
    await db.flush()
    portal = vendor_portal(db)

    row = await portal.update_job_string_async(
        job.id, seed.strings[0].id, "maschinell"
    )

    assert row.in_job is True
    assert row.vendor_reviewed is True
    assert row.translation_source == "Marketplace"

    stored = (
        await db.execute(
            select(LocalizationTranslation).where(
                LocalizationTranslation.string_id == seed.strings[0].id
            )
        )
    ).scalar_one()
    assert stored.translation_source == "Marketplace"
    assert stored.raw_mt_text == "maschinell"

    reloaded = (
        await db.execute(
            select(TranslationJob).where(TranslationJob.id == job.id)
        )
    ).scalar_one()
    assert reloaded.status == "InProgress"


@pytest.mark.asyncio
async def test_update_job_string_on_approved_string_is_rejected(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    job = await _seed_job(db, seed.project.id, vendor.id, "InProgress")
    db.add(
        LocalizationTranslation(
            string_id=seed.strings[0].id,
            locale_code="de-DE",
            target_text="genehmigt",
            stage="Approved",
            translation_source="Marketplace",
            needs_review=False,
            updated_at=datetime.now(UTC),
        )
    )
    await db.flush()
    portal = vendor_portal(db)

    with pytest.raises(InvalidJobStateException, match="already approved"):
        await portal.update_job_string_async(job.id, seed.strings[0].id, "neu")


@pytest.mark.asyncio
async def test_submit_job_for_review_with_unreviewed_machine_output_is_rejected_until_accepted(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    job = await _seed_job(db, seed.project.id, vendor.id, "InProgress")
    now = datetime.now(UTC)
    db.add_all(
        [
            LocalizationTranslation(
                string_id=seed.strings[0].id,
                locale_code="de-DE",
                target_text="done",
                stage="Translated",
                translation_source="Marketplace",
                needs_review=False,
                updated_at=now,
            ),
            LocalizationTranslation(
                string_id=seed.strings[1].id,
                locale_code="de-DE",
                target_text="maschinell",
                stage="Translated",
                translation_source="AI",
                needs_review=False,
                updated_at=now,
            ),
        ]
    )
    await db.flush()
    portal = vendor_portal(db)

    with pytest.raises(
        InvalidJobStateException,
        match="1 machine-translated strings still need review",
    ):
        await portal.submit_job_for_review_async(job.id)

    await portal.update_job_string_async(job.id, seed.strings[1].id, "maschinell")
    row = await portal.submit_job_for_review_async(job.id)
    assert row.status == "SubmittedForReview"


@pytest.mark.asyncio
async def test_run_mt_optimize_skips_vendor_edited_translations(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    now = datetime.now(UTC)
    db.add_all(
        [
            LocalizationTranslation(
                string_id=seed.strings[0].id,
                locale_code="de-DE",
                target_text="vendor text",
                raw_mt_text="roh1",
                stage="Translated",
                translation_source="Marketplace",
                needs_review=False,
                updated_at=now,
            ),
            LocalizationTranslation(
                string_id=seed.strings[1].id,
                locale_code="de-DE",
                target_text="alt2",
                raw_mt_text="roh2",
                stage="Translated",
                translation_source="AI",
                needs_review=False,
                updated_at=now,
            ),
        ]
    )
    await db.flush()

    handler = _CountingOptimizeHandler()
    flow = WorkflowService(
        db,
        FakeTranslationProvider(),
        MtOptimizeService(_optimize_client(handler)),
        FakeQualityScorer(),
        AutoRoutingService(),
        jobs(db),
        None,
        None,
    )

    step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Run MT Optimize")
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "1 strings optimized"
    assert handler.call_count == 1

    vendor = (
        await db.execute(
            select(LocalizationTranslation).where(
                LocalizationTranslation.string_id == seed.strings[0].id
            )
        )
    ).scalar_one()
    assert vendor.target_text == "vendor text"
    assert vendor.translation_source == "Marketplace"
