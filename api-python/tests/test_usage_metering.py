"""Translated from UsageMeteringTests.cs.

Uses httpx.MockTransport as the fake AI service (no real network calls).
"""

from __future__ import annotations

from collections import deque
from datetime import UTC, datetime
from decimal import Decimal

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.localization.localization_provider_rate import LocalizationProviderRate
from app.models.localization.localization_translation import LocalizationTranslation
from app.models.localization.localization_usage_event import LocalizationUsageEvent
from app.models.localization.usage_constants import (
    UsageMeters,
    UsageOperations,
    UsageUnitKinds,
)
from app.schemas.localization_dtos import AddWorkflowStepRequest
from app.services.localization.auto_routing_service import AutoRoutingService
from app.services.localization.i_quality_scorer import QualityScoreResult
from app.services.localization.localization_ai_client import (
    LocalizationAiClient,
    LocalizationAiException,
)
from app.services.localization.mt_optimize_service import MtOptimizeService
from app.services.localization.usage_metering_service import (
    UsageCallRecord,
    UsageMeteringService,
)
from app.services.localization.workflow_service import WorkflowService
from app.settings import LocalizationAiSettings

from .localization_fixture import (
    FakeQualityScorer,
    FakeTranslationProvider,
    jobs,
    seed_project,
)
from .localization_fixture import workflow as unmetered_workflow


class _FakeAiHandler:
    """Queued fake for the localization-ai HTTP contract."""

    def __init__(self) -> None:
        self._queued: dict[str, deque[tuple[int, str]]] = {}

    def queue_json(self, path: str, payload: str) -> None:
        self._queued.setdefault(path, deque()).append((200, payload))

    def handler(self, request: httpx.Request) -> httpx.Response:
        path = request.url.path.strip("/")
        queue = self._queued.get(path)
        if queue:
            status, text = queue.popleft()
            return httpx.Response(status, text=text)
        return httpx.Response(404, text=f"no scripted response for {path}")


class _TokenScorer:
    @property
    def is_configured(self) -> bool:
        return True

    async def score_async(
        self, source_text: str, target_text: str, target_locale: str
    ) -> QualityScoreResult:
        return QualityScoreResult(4, [], 20, 8)


class _ThrowingScorer:
    def __init__(self, input_tokens: int, output_tokens: int) -> None:
        self._input_tokens = input_tokens
        self._output_tokens = output_tokens

    @property
    def is_configured(self) -> bool:
        return True

    async def score_async(
        self, source_text: str, target_text: str, target_locale: str
    ) -> QualityScoreResult:
        exc = LocalizationAiException(
            "The QPS judge fell back without producing a score."
        )
        exc.input_tokens = self._input_tokens
        exc.output_tokens = self._output_tokens
        raise exc


def _ai_client(handler: _FakeAiHandler) -> LocalizationAiClient:
    options = LocalizationAiSettings(
        **{"LocalizationAi__BaseUrl": "http://ai/"}
    )
    http_client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler.handler), base_url="http://ai/"
    )
    return LocalizationAiClient(options=options, http_client=http_client)


def _workflow_with_metering(
    db: AsyncSession,
    provider: FakeTranslationProvider | None = None,
    optimize: MtOptimizeService | None = None,
    scorer: FakeQualityScorer | _TokenScorer | _ThrowingScorer | None = None,
) -> WorkflowService:
    return WorkflowService(
        db,
        provider or FakeTranslationProvider(),
        optimize or MtOptimizeService(),
        scorer or FakeQualityScorer(),
        AutoRoutingService(),
        jobs(db),
        None,
        UsageMeteringService(db),
    )


@pytest.mark.asyncio
async def test_auto_translate_records_one_event_per_translated_string_locale(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    db.add(
        LocalizationTranslation(
            string_id=seed.strings[0].id,
            locale_code="de-DE",
            target_text="schon da",
            stage="Translated",
            translation_source="Manual",
            needs_review=False,
            updated_at=datetime.now(UTC),
        )
    )
    await db.flush()
    flow = _workflow_with_metering(db)

    step = await flow.add_step_async(
        seed.project.slug,
        AddWorkflowStepRequest(action="Auto-Translate via Azure Translator"),
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "3 strings translated via Azure Translator"

    events = (
        await db.execute(select(LocalizationUsageEvent))
    ).scalars().all()
    assert len(events) == 3
    assert all(e.meter == UsageMeters.MACHINE_TRANSLATION for e in events)
    assert all(e.operation == UsageOperations.MT_DRAFT for e in events)
    assert all(e.project_id == seed.project.id for e in events)
    assert all(e.workflow_step_id == step.id for e in events)
    assert all(e.succeeded for e in events)
    assert all(not e.cache_hit for e in events)
    assert all(e.units_out is None for e in events)
    assert all(e.cost_usd == Decimal(0) for e in events)

    german = [e for e in events if e.locale_code == "de-DE"]
    assert len(german) == 1
    assert german[0].units == len("Goodbye moon")
    assert sorted(
        e.units for e in events if e.locale_code == "fr-FR"
    ) == [len("Hello world"), len("Goodbye moon")]


@pytest.mark.asyncio
async def test_mt_optimize_records_tokens_and_zero_cost_cache_hit(
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
                target_text="alt1",
                raw_mt_text="roh1",
                stage="Translated",
                translation_source="AI",
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
    db.add_all(
        [
            LocalizationProviderRate(
                meter=UsageMeters.LLM_OPTIMIZE,
                unit_kind=UsageUnitKinds.INPUT_TOKEN,
                usd_per_million=Decimal(2000),
                valid_from=datetime(2026, 1, 1, tzinfo=UTC),
            ),
            LocalizationProviderRate(
                meter=UsageMeters.LLM_OPTIMIZE,
                unit_kind=UsageUnitKinds.OUTPUT_TOKEN,
                usd_per_million=Decimal(4000),
                valid_from=datetime(2026, 1, 1, tzinfo=UTC),
            ),
        ]
    )
    await db.flush()

    handler = _FakeAiHandler()
    handler.queue_json(
        "translate-and-optimize",
        '{"optimizedTranslation":"opt-a","cacheHit":false,"checks":{},"inputTokens":10,'
        '"outputTokens":5,"tokensUsed":15,"latencyMs":3,"fallback":false}',
    )
    handler.queue_json(
        "translate-and-optimize",
        '{"optimizedTranslation":"opt-b","cacheHit":true,"checks":{},"inputTokens":7,'
        '"outputTokens":3,"tokensUsed":10,"latencyMs":1,"fallback":false}',
    )
    flow = _workflow_with_metering(
        db, optimize=MtOptimizeService(_ai_client(handler))
    )

    step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Run MT Optimize")
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "2 strings optimized"

    events = (
        await db.execute(select(LocalizationUsageEvent))
    ).scalars().all()
    assert len(events) == 2
    assert all(e.meter == UsageMeters.LLM_OPTIMIZE for e in events)
    assert all(e.operation == UsageOperations.MT_OPTIMIZE for e in events)

    cached = [e for e in events if e.cache_hit]
    assert len(cached) == 1
    assert cached[0].cost_usd == Decimal(0)
    fresh = [e for e in events if not e.cache_hit]
    assert len(fresh) == 1
    assert fresh[0].units == 10
    assert fresh[0].units_out == 5
    assert fresh[0].cost_usd == Decimal("0.04")


@pytest.mark.asyncio
async def test_qps_score_records_both_calls_with_tokens(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    db.add(
        LocalizationTranslation(
            string_id=seed.strings[0].id,
            locale_code="de-DE",
            target_text="t1",
            raw_mt_text="r1",
            stage="Translated",
            translation_source="AI",
            needs_review=False,
            updated_at=datetime.now(UTC),
        )
    )
    await db.flush()
    flow = _workflow_with_metering(db, scorer=_TokenScorer())

    step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Score Quality")
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "1 strings scored"

    events = (
        await db.execute(select(LocalizationUsageEvent))
    ).scalars().all()
    assert len(events) == 2
    assert all(e.meter == UsageMeters.LLM_SCORE for e in events)
    assert all(e.operation == UsageOperations.QPS_SCORE for e in events)
    assert all(e.succeeded for e in events)
    assert all(e.units == 20 for e in events)
    assert all(e.units_out == 8 for e in events)


@pytest.mark.asyncio
async def test_qps_score_failed_call_with_tokens_records_unsuccessful_event(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    db.add(
        LocalizationTranslation(
            string_id=seed.strings[0].id,
            locale_code="de-DE",
            target_text="t1",
            stage="Translated",
            translation_source="AI",
            needs_review=False,
            updated_at=datetime.now(UTC),
        )
    )
    await db.flush()
    flow = _workflow_with_metering(db, scorer=_ThrowingScorer(5, 2))

    step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Score Quality")
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "0 strings scored, 1 failed"

    failed = (await db.execute(select(LocalizationUsageEvent))).scalar_one()
    assert failed.meter == UsageMeters.LLM_SCORE
    assert not failed.succeeded
    assert failed.units == 5
    assert failed.units_out == 2


@pytest.mark.asyncio
async def test_qps_score_failed_call_without_tokens_records_nothing(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    db.add(
        LocalizationTranslation(
            string_id=seed.strings[0].id,
            locale_code="de-DE",
            target_text="t1",
            stage="Translated",
            translation_source="AI",
            needs_review=False,
            updated_at=datetime.now(UTC),
        )
    )
    await db.flush()
    flow = _workflow_with_metering(db, scorer=_ThrowingScorer(0, 0))

    step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Score Quality")
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "0 strings scored, 1 failed"
    events = (
        await db.execute(select(LocalizationUsageEvent))
    ).scalars().all()
    assert events == []


@pytest.mark.asyncio
async def test_usage_cost_uses_rate_in_force_at_event_time(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    db.add_all(
        [
            LocalizationProviderRate(
                meter=UsageMeters.LLM_SCORE,
                unit_kind=UsageUnitKinds.INPUT_TOKEN,
                usd_per_million=Decimal(1000),
                valid_from=datetime(2026, 1, 10, tzinfo=UTC),
            ),
            LocalizationProviderRate(
                meter=UsageMeters.LLM_SCORE,
                unit_kind=UsageUnitKinds.INPUT_TOKEN,
                usd_per_million=Decimal(2000),
                valid_from=datetime(2026, 6, 10, tzinfo=UTC),
            ),
            LocalizationProviderRate(
                meter=UsageMeters.LLM_SCORE,
                unit_kind=UsageUnitKinds.OUTPUT_TOKEN,
                usd_per_million=Decimal(4000),
                valid_from=datetime(2026, 1, 1, tzinfo=UTC),
            ),
        ]
    )
    await db.flush()
    metering = UsageMeteringService(db)

    call = UsageCallRecord(
        project_id=seed.project.id,
        workflow_step_id=None,
        meter=UsageMeters.LLM_SCORE,
        operation=UsageOperations.QPS_SCORE,
        locale_code="de-DE",
        units=100,
        units_out=10,
        cache_hit=False,
        succeeded=True,
    )
    await metering.record_async(call, datetime(2026, 3, 5, 12, 0, 0, tzinfo=UTC))
    await metering.record_async(call, datetime(2026, 7, 5, 12, 0, 0, tzinfo=UTC))
    await db.flush()

    costs = (
        await db.execute(
            select(LocalizationUsageEvent.cost_usd).order_by(
                LocalizationUsageEvent.occurred_at
            )
        )
    ).scalars().all()
    assert list(costs) == [Decimal("0.14"), Decimal("0.24")]


@pytest.mark.asyncio
async def test_usage_cost_without_rate_is_zero_and_listed_missing(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
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
        datetime(2026, 3, 5, 12, 0, 0, tzinfo=UTC),
    )
    await db.flush()

    stored = (await db.execute(select(LocalizationUsageEvent))).scalar_one()
    assert stored.cost_usd == Decimal(0)

    summary = await metering.get_summary_async(seed.project.slug, 2026, 3)
    assert len(summary.rates_missing) == 1
    assert summary.rates_missing[0].meter == UsageMeters.MACHINE_TRANSLATION
    assert summary.rates_missing[0].unit_kind == UsageUnitKinds.CHAR


@pytest.mark.asyncio
async def test_usage_summary_totals_for_one_month_and_project_are_exact(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    first = await seed_project(db, "slug-a")
    second = await seed_project(db, "slug-b")
    metering = UsageMeteringService(db)

    def mt_call(project_id: int, locale: str, units: int) -> UsageCallRecord:
        return UsageCallRecord(
            project_id=project_id,
            workflow_step_id=None,
            meter=UsageMeters.MACHINE_TRANSLATION,
            operation=UsageOperations.MT_DRAFT,
            locale_code=locale,
            units=units,
            units_out=None,
            cache_hit=False,
            succeeded=True,
        )

    await metering.record_async(
        mt_call(first.project.id, "de-DE", 100),
        datetime(2026, 3, 5, 12, 0, 0, tzinfo=UTC),
    )
    await metering.record_async(
        UsageCallRecord(
            project_id=first.project.id,
            workflow_step_id=None,
            meter=UsageMeters.LLM_SCORE,
            operation=UsageOperations.QPS_SCORE,
            locale_code="de-DE",
            units=10,
            units_out=2,
            cache_hit=False,
            succeeded=True,
        ),
        datetime(2026, 3, 6, 12, 0, 0, tzinfo=UTC),
    )
    await metering.record_async(
        mt_call(first.project.id, "fr-FR", 50),
        datetime(2026, 4, 2, 12, 0, 0, tzinfo=UTC),
    )
    await metering.record_async(
        mt_call(second.project.id, "de-DE", 1000),
        datetime(2026, 3, 7, 12, 0, 0, tzinfo=UTC),
    )
    await db.flush()

    summary = await metering.get_summary_async("slug-a", 2026, 3)
    assert summary.month == "2026-03"
    assert summary.project_slug == "slug-a"

    mt = [m for m in summary.meters if m.meter == UsageMeters.MACHINE_TRANSLATION]
    assert len(mt) == 1
    assert mt[0].calls == 1
    assert mt[0].failed_calls == 0
    assert mt[0].cache_hits == 0
    assert mt[0].units == 100
    assert mt[0].units_out is None
    assert mt[0].cost_usd == Decimal(0)

    score = [m for m in summary.meters if m.meter == UsageMeters.LLM_SCORE]
    assert len(score) == 1
    assert score[0].calls == 1
    assert score[0].units == 10
    assert score[0].units_out == 2

    assert len(summary.by_operation) == 2
    de = [
        row
        for row in summary.by_locale
        if row.locale_code == "de-DE" and row.meter == UsageMeters.MACHINE_TRANSLATION
    ]
    assert len(de) == 1
    assert de[0].units == 100
    assert sorted(d.date for d in summary.by_day) == ["2026-03-05", "2026-03-06"]
    assert len(summary.rates_missing) == 3

    everything = await metering.get_summary_async(None, 2026, 3)
    assert everything.project_slug is None
    assert (
        next(
            m for m in everything.meters if m.meter == UsageMeters.MACHINE_TRANSLATION
        ).units
        == 1100
    )
    assert (
        next(
            m for m in everything.meters if m.meter == UsageMeters.LLM_SCORE
        ).units
        == 10
    )


@pytest.mark.asyncio
async def test_workflow_without_metering_runs_every_action(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    flow = unmetered_workflow(db)

    async def run(action: str) -> str | None:
        step = await flow.add_step_async(
            seed.project.slug, AddWorkflowStepRequest(action=action)
        )
        return (await flow.run_step_async(seed.project.slug, step.id)).last_run_outcome

    assert await run("Create Translation Jobs") == "0 jobs created, 2 skipped"
    assert (
        await run("Auto-Translate via Azure Translator")
        == "4 strings translated via Azure Translator"
    )
    assert await run("Mark Translated") == "0 strings affected"
    assert await run("Send to Review") == "4 strings affected"
    assert await run("Approve") == "4 strings affected"

    optimize_step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Run MT Optimize")
    )
    with pytest.raises(NotImplementedError):
        await flow.run_step_async(seed.project.slug, optimize_step.id)

    assert await run("Score Quality") == "0 strings scored"

    route_step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Auto-Route")
    )
    with pytest.raises(NotImplementedError):
        await flow.run_step_async(seed.project.slug, route_step.id)

    events = (
        await db.execute(select(LocalizationUsageEvent))
    ).scalars().all()
    assert events == []
