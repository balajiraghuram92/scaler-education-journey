"""Translated from UsageControlsTests.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.localization.ledger_entry import LedgerEntry
from app.models.localization.localization_locale import LocalizationLocale
from app.models.localization.localization_project import LocalizationProject
from app.models.localization.localization_string import LocalizationString
from app.models.localization.localization_translation import LocalizationTranslation
from app.models.localization.localization_usage_cap import LocalizationUsageCap
from app.models.localization.localization_usage_event import LocalizationUsageEvent
from app.models.localization.usage_constants import (
    UsageCapKinds,
    UsageMeters,
    UsageOperations,
)
from app.schemas.localization_dtos import AddWorkflowStepRequest
from app.services.localization.auto_routing_service import AutoRoutingService
from app.services.localization.i_quality_scorer import QualityScoreResult
from app.services.localization.localization_exceptions import (
    LocalizationAiDisabledException,
    LocalizationUsageCapReachedException,
)
from app.services.localization.mt_optimize_service import MtOptimizeService
from app.services.localization.usage_metering_service import (
    UsageCallRecord,
    UsageMeteringService,
)
from app.services.localization.workflow_service import WorkflowService

from .localization_fixture import (
    FakeQualityScorer,
    FakeTranslationProvider,
    jobs,
    seed_project,
)
from .localization_fixture import workflow as fixture_workflow


class _CountingTranslationProvider:
    def __init__(self) -> None:
        self.call_count = 0

    async def translate_async(
        self, source_text: str, source_locale: str, target_locale: str
    ) -> str:
        self.call_count += 1
        return f"[{target_locale}]{source_text}"


class _CountingScorer:
    def __init__(self) -> None:
        self.call_count = 0

    @property
    def is_configured(self) -> bool:
        return True

    async def score_async(
        self, source_text: str, target_text: str, target_locale: str
    ) -> QualityScoreResult:
        self.call_count += 1
        return QualityScoreResult(4, [], 20, 8)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "action",
    [
        "Auto-Translate via Azure Translator",
        "Run MT Optimize",
        "Score Quality",
        "Auto-Route",
    ],
)
async def test_disabled_project_provider_actions_throw(
    scratch_session: AsyncSession, action: str
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    seed.project.ai_enabled = False
    await db.flush()
    flow = fixture_workflow(db)

    step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action=action)
    )
    with pytest.raises(LocalizationAiDisabledException) as exc_info:
        await flow.run_step_async(seed.project.slug, step.id)
    assert exc_info.value.project_slug == seed.project.slug


@pytest.mark.asyncio
async def test_mt_cap_already_reached_throws_without_calling_provider(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    db.add(
        LocalizationUsageCap(
            project_id=seed.project.id,
            kind=UsageCapKinds.MACHINE_TRANSLATION,
            monthly_limit=100,
            updated_at=datetime.now(UTC),
        )
    )
    metering = UsageMeteringService(db)
    await metering.record_async(
        UsageCallRecord(
            project_id=seed.project.id,
            workflow_step_id=None,
            meter=UsageMeters.MACHINE_TRANSLATION,
            operation=UsageOperations.MT_DRAFT,
            locale_code="de-DE",
            units=100,
            units_out=None,
            cache_hit=False,
            succeeded=True,
        ),
        datetime.now(UTC),
    )
    await db.flush()

    provider = _CountingTranslationProvider()
    flow = WorkflowService(
        db,
        provider,
        MtOptimizeService(),
        FakeQualityScorer(),
        AutoRoutingService(),
        jobs(db),
        None,
        metering,
    )

    step = await flow.add_step_async(
        seed.project.slug,
        AddWorkflowStepRequest(action="Auto-Translate via Azure Translator"),
    )
    with pytest.raises(LocalizationUsageCapReachedException) as exc_info:
        await flow.run_step_async(seed.project.slug, step.id)

    assert provider.call_count == 0
    assert exc_info.value.kind == UsageCapKinds.MACHINE_TRANSLATION
    assert exc_info.value.used == 100
    assert exc_info.value.limit == 100


@pytest.mark.asyncio
async def test_mt_cap_reached_part_way_skips_before_and_after_keeping_translated(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    project = LocalizationProject(
        slug="cap-mt", name="Cap MT", source_locale="en-US", ai_enabled=True
    )
    db.add(project)
    await db.flush()
    db.add(
        LocalizationLocale(
            project_id=project.id, locale_code="de-DE", display_name="German"
        )
    )
    for length in (25, 11, 12):
        db.add(
            LocalizationString(
                project_id=project.id,
                source_text="x" * length,
                created_at=datetime.now(UTC),
            )
        )
    db.add(
        LocalizationUsageCap(
            project_id=project.id,
            kind=UsageCapKinds.MACHINE_TRANSLATION,
            monthly_limit=20,
            updated_at=datetime.now(UTC),
        )
    )
    await db.flush()

    provider = _CountingTranslationProvider()
    flow = WorkflowService(
        db,
        provider,
        MtOptimizeService(),
        FakeQualityScorer(),
        AutoRoutingService(),
        jobs(db),
        None,
        UsageMeteringService(db),
    )

    step = await flow.add_step_async(
        project.slug,
        AddWorkflowStepRequest(action="Auto-Translate via Azure Translator"),
    )
    ran = await flow.run_step_async(project.slug, step.id)

    assert (
        ran.last_run_outcome
        == "1 strings translated via Azure Translator, 2 skipped: monthly "
        "machine-translation cap reached (11 of 20)"
    )
    assert provider.call_count == 1

    translations = (
        await db.execute(select(LocalizationTranslation))
    ).scalars().all()
    kept = [t for t in translations if t.target_text and t.target_text.strip()]
    assert len(kept) == 1
    assert kept[0].target_text == "[de-DE]" + "x" * 11

    events = (
        await db.execute(select(LocalizationUsageEvent))
    ).scalars().all()
    assert len(events) == 1


@pytest.mark.asyncio
async def test_llm_cap_crossing_call_completes_and_later_calls_stop(
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
                target_text="t1",
                stage="Translated",
                translation_source="AI",
                needs_review=False,
                updated_at=now,
            ),
            LocalizationTranslation(
                string_id=seed.strings[1].id,
                locale_code="de-DE",
                target_text="t2",
                stage="Translated",
                translation_source="AI",
                needs_review=False,
                updated_at=now,
            ),
        ]
    )
    db.add(
        LocalizationUsageCap(
            project_id=seed.project.id,
            kind=UsageCapKinds.LLM,
            monthly_limit=25,
            updated_at=now,
        )
    )
    await db.flush()

    scorer = _CountingScorer()
    flow = WorkflowService(
        db,
        FakeTranslationProvider(),
        MtOptimizeService(),
        scorer,
        AutoRoutingService(),
        jobs(db),
        None,
        UsageMeteringService(db),
    )

    step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Score Quality")
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert (
        ran.last_run_outcome
        == "1 strings scored, 1 skipped: monthly llm cap reached (28 of 25)"
    )
    assert scorer.call_count == 1

    scored = (await db.execute(select(LocalizationUsageEvent))).scalar_one()
    assert scored.succeeded
    assert scored.units == 20
    assert scored.units_out == 8


@pytest.mark.asyncio
async def test_high_cap_run_matches_uncapped_behaviour(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    db.add(
        LocalizationUsageCap(
            project_id=seed.project.id,
            kind=UsageCapKinds.MACHINE_TRANSLATION,
            monthly_limit=1000000000,
            updated_at=datetime.now(UTC),
        )
    )
    await db.flush()

    flow = WorkflowService(
        db,
        FakeTranslationProvider(),
        MtOptimizeService(),
        FakeQualityScorer(),
        AutoRoutingService(),
        jobs(db),
        None,
        UsageMeteringService(db),
    )

    step = await flow.add_step_async(
        seed.project.slug,
        AddWorkflowStepRequest(action="Auto-Translate via Azure Translator"),
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "4 strings translated via Azure Translator"
    assert ran.last_run_outcome is not None
    assert "skipped" not in ran.last_run_outcome

    events = (
        await db.execute(select(LocalizationUsageEvent))
    ).scalars().all()
    assert len(events) == 4
    assert all(e.meter == UsageMeters.MACHINE_TRANSLATION for e in events)
    assert all(e.operation == UsageOperations.MT_DRAFT for e in events)
    assert all(e.workflow_step_id == step.id for e in events)
    assert all(e.cost_usd == Decimal(0) for e in events)

    # R3 removed the AI ledger writes: the ledger stays empty.
    ledger = (await db.execute(select(LedgerEntry))).scalars().all()
    assert ledger == []
