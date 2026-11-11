"""Translated from LocalizationAiWorkflowTests.cs.

Uses httpx.MockTransport as the fake AI service (no real network calls).

NOTE: the RunMtOptimize/ScoreQps/AutoTranslate tests below touch the
localization_glossary_terms table and the raw_mt_text/raw_mt_qps_score
columns, which have no EF migration yet (Findings 2-3). They pass only after
the reviewer generates and applies the pending LA1 migration; until then
they fail on a real scratch database in Python exactly as the equivalent
paths fail in C#.
"""

from __future__ import annotations

import json
from collections import deque
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.localization.glossary_term import GlossaryTerm
from app.models.localization.ledger_entry import LedgerEntry
from app.models.localization.localization_translation import LocalizationTranslation
from app.schemas.localization_dtos import AddWorkflowStepRequest
from app.services.localization.auto_routing_service import AutoRoutingService
from app.services.localization.localization_ai_client import LocalizationAiClient
from app.services.localization.mt_optimize_service import MtOptimizeService
from app.services.localization.qps_scoring_service import QpsScoringService
from app.services.localization.workflow_service import WorkflowService
from app.settings import LocalizationAiSettings

from .localization_fixture import (
    FakeTranslationProvider,
    marketplace,
    seed_project,
)


class FakeAiTransport:
    """Queued + responder-based fake for the localization-ai HTTP contract."""

    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []
        self.bodies: list[str] = []
        self._queued: dict[str, deque[tuple[int, str]]] = {}
        self._responders: dict[str, Callable[[str], str]] = {}

    def queue_json(self, path: str, payload: str) -> None:
        self._queued.setdefault(path, deque()).append((200, payload))

    def queue_status(self, path: str, status: int) -> None:
        self._queued.setdefault(path, deque()).append((status, "boom"))

    def respond(self, path: str, responder: Callable[[str], str]) -> None:
        self._responders[path] = responder

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        body = request.content.decode("utf-8") if request.content else ""
        self.bodies.append(body)
        path = request.url.path.strip("/")
        if path in self._responders:
            return httpx.Response(200, text=self._responders[path](body))
        queue = self._queued.get(path)
        if queue:
            status, text = queue.popleft()
            return httpx.Response(status, text=text)
        return httpx.Response(404, text=f"no scripted response for {path}")


def _ai_options() -> LocalizationAiSettings:
    return LocalizationAiSettings(
        **{
            "LocalizationAi__BaseUrl": "http://ai/",
            "LocalizationAi__SharedSecret": "test-secret",
            "LocalizationAi__ChatPricePer1kInputTokensUsd": Decimal("1000"),
            "LocalizationAi__ChatPricePer1kOutputTokensUsd": Decimal("2000"),
            "LocalizationAi__LegacyMtPricePerCharUsd": Decimal("0.00002"),
        }
    )


def _ai_client(
    fake: FakeAiTransport, options: LocalizationAiSettings
) -> LocalizationAiClient:
    http_client = httpx.AsyncClient(
        transport=httpx.MockTransport(fake.handler), base_url="http://ai/"
    )
    return LocalizationAiClient(options=options, http_client=http_client)


def _workflow(
    db: AsyncSession, client: LocalizationAiClient, options: LocalizationAiSettings
) -> WorkflowService:
    return WorkflowService(
        db,
        FakeTranslationProvider(),
        MtOptimizeService(client),
        QpsScoringService(client),
        AutoRoutingService(client),
        marketplace(db),
        options,
    )


def _respond_echo_optimize(fake: FakeAiTransport) -> None:
    def responder(body: str) -> str:
        raw = json.loads(body)["rawMtText"]
        return (
            '{"optimizedTranslation":"opt:' + raw + '","cacheHit":false,"checks":{},'
            '"inputTokens":10,"outputTokens":5,"embeddingTokens":0,"tokensUsed":15,'
            '"latencyMs":3,"costUsd":0.001,"fallback":false}'
        )

    fake.respond("translate-and-optimize", responder)


@pytest.mark.asyncio
async def test_run_mt_optimize_updates_targets_and_writes_token_ledger(
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
    db.add(
        GlossaryTerm(
            project_id=seed.project.id,
            locale_code="de-DE",
            source_term="Hello",
            target_term="Hallo",
        )
    )
    await db.flush()

    fake = FakeAiTransport()
    _respond_echo_optimize(fake)
    options = _ai_options()
    flow = _workflow(db, _ai_client(fake, options), options)

    step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Run MT Optimize")
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "2 strings optimized"

    targets = (
        await db.execute(
            select(LocalizationTranslation.target_text).order_by(
                LocalizationTranslation.target_text
            )
        )
    ).scalars().all()
    assert list(targets) == ["opt:roh1", "opt:roh2"]

    entry = (await db.execute(select(LedgerEntry))).scalar_one()
    assert entry.source == "AI"
    assert entry.unit_type == "tokens"
    assert entry.units_consumed == 30
    assert entry.real_cost_usd == Decimal("40")

    assert len(fake.requests) == 2
    for request in fake.requests:
        assert request.headers.get("x-api-key") == "test-secret"
    for body in fake.bodies:
        assert "Hallo" in body


@pytest.mark.asyncio
async def test_run_mt_optimize_partial_failure_continues_and_counts(
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
    await db.flush()

    fake = FakeAiTransport()
    fake.queue_status("translate-and-optimize", 500)
    fake.queue_json(
        "translate-and-optimize",
        '{"optimizedTranslation":"opt-ok","cacheHit":false,"checks":{},"inputTokens":10,'
        '"outputTokens":5,"embeddingTokens":0,"tokensUsed":15,"latencyMs":3,"costUsd":0.001,"fallback":false}',
    )
    options = _ai_options()
    flow = _workflow(db, _ai_client(fake, options), options)

    step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Run MT Optimize")
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "1 strings optimized, 1 failed"

    targets = (
        await db.execute(
            select(LocalizationTranslation.target_text).order_by(
                LocalizationTranslation.target_text
            )
        )
    ).scalars().all()
    assert "opt-ok" in list(targets)

    entry = (await db.execute(select(LedgerEntry))).scalar_one()
    assert entry.units_consumed == 15


@pytest.mark.asyncio
async def test_score_qps_stores_score_and_raw_score_once(
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
                raw_mt_text="r1",
                stage="Translated",
                translation_source="AI",
                needs_review=False,
                updated_at=now,
            ),
            LocalizationTranslation(
                string_id=seed.strings[1].id,
                locale_code="de-DE",
                target_text="manual",
                raw_mt_text="r2",
                stage="Translated",
                translation_source="Manual",
                needs_review=False,
                updated_at=now,
            ),
        ]
    )
    await db.flush()

    fake = FakeAiTransport()
    fake.queue_json(
        "qps-score",
        '{"score":85,"flaggedIssues":["tone"],"inputTokens":20,"outputTokens":8,'
        '"tokensUsed":28,"latencyMs":4,"costUsd":0.002,"fallback":false}',
    )
    fake.queue_json(
        "qps-score",
        '{"score":60,"flaggedIssues":[],"inputTokens":20,"outputTokens":8,'
        '"tokensUsed":28,"latencyMs":4,"costUsd":0.002,"fallback":false}',
    )
    options = _ai_options()
    flow = _workflow(db, _ai_client(fake, options), options)

    step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Score QPS")
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "1 strings scored"
    assert len(fake.requests) == 2

    ai_row = (
        await db.execute(
            select(LocalizationTranslation).where(
                LocalizationTranslation.string_id == seed.strings[0].id
            )
        )
    ).scalar_one()
    assert ai_row.qps_score == 85
    assert ai_row.raw_mt_qps_score == 60

    manual_row = (
        await db.execute(
            select(LocalizationTranslation).where(
                LocalizationTranslation.string_id == seed.strings[1].id
            )
        )
    ).scalar_one()
    assert manual_row.qps_score is None
    assert manual_row.raw_mt_qps_score is None


@pytest.mark.asyncio
async def test_score_qps_does_not_rescore_raw_when_already_set(
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
            raw_mt_qps_score=55,
            stage="Translated",
            translation_source="AI",
            needs_review=False,
            updated_at=datetime.now(UTC),
        )
    )
    await db.flush()

    fake = FakeAiTransport()
    fake.queue_json(
        "qps-score",
        '{"score":90,"flaggedIssues":[],"inputTokens":1,"outputTokens":1,'
        '"tokensUsed":2,"latencyMs":1,"costUsd":0,"fallback":false}',
    )
    options = _ai_options()
    flow = _workflow(db, _ai_client(fake, options), options)

    step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Score QPS")
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "1 strings scored"
    assert len(fake.requests) == 1

    row = (await db.execute(select(LocalizationTranslation))).scalar_one()
    assert row.qps_score == 90
    assert row.raw_mt_qps_score == 55


@pytest.mark.asyncio
async def test_auto_route_sets_needs_review_from_project_threshold(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    seed.project.qps_threshold = 75
    now = datetime.now(UTC)
    db.add_all(
        [
            LocalizationTranslation(
                string_id=seed.strings[0].id,
                locale_code="de-DE",
                target_text="t1",
                stage="Translated",
                translation_source="AI",
                qps_score=80,
                needs_review=False,
                updated_at=now,
            ),
            LocalizationTranslation(
                string_id=seed.strings[1].id,
                locale_code="de-DE",
                target_text="t2",
                stage="Translated",
                translation_source="AI",
                qps_score=70,
                needs_review=False,
                updated_at=now,
            ),
            LocalizationTranslation(
                string_id=seed.strings[0].id,
                locale_code="fr-FR",
                target_text="t3",
                stage="Translated",
                translation_source="AI",
                qps_score=None,
                needs_review=False,
                updated_at=now,
            ),
        ]
    )
    await db.flush()

    fake = FakeAiTransport()

    def responder(body: str) -> str:
        payload = json.loads(body)
        needs = payload["qpsScore"] < payload["projectThreshold"]
        return (
            '{"needsReview":' + ("true" if needs else "false")
            + ',"reasons":[],"tokensUsed":0,"latencyMs":0,"fallback":false}'
        )

    fake.respond("auto-route", responder)
    options = _ai_options()
    flow = _workflow(db, _ai_client(fake, options), options)

    step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Auto-Route")
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "2 strings processed, 1 flagged for review"
    assert len(fake.requests) == 2
    for body in fake.bodies:
        assert '"projectThreshold":75' in body

    rows = (
        await db.execute(
            select(LocalizationTranslation).order_by(
                LocalizationTranslation.qps_score
            )
        )
    ).scalars().all()
    de_scores = [
        row.qps_score for row in rows if row.locale_code == "de-DE"
    ]
    assert de_scores == [70, 80]
    by_score = {row.qps_score: row for row in rows if row.qps_score is not None}
    assert by_score[70].needs_review is True
    assert by_score[80].needs_review is False
    fr_row = next(row for row in rows if row.locale_code == "fr-FR")
    assert fr_row.needs_review is False


@pytest.mark.asyncio
async def test_auto_translate_writes_characters_ledger_entry(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    options = _ai_options()
    # No AI calls happen on this path; the client is never touched.
    flow = _workflow(db, _ai_client(FakeAiTransport(), options), options)

    step = await flow.add_step_async(
        seed.project.slug,
        AddWorkflowStepRequest(action="Auto-Translate via Google MT"),
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "4 strings translated via Google MT"

    rows = (await db.execute(select(LocalizationTranslation))).scalars().all()
    assert len(rows) == 4
    for row in rows:
        assert row.target_text == row.raw_mt_text

    entry = (await db.execute(select(LedgerEntry))).scalar_one()
    assert entry.source == "AI"
    assert entry.unit_type == "characters"
    assert entry.units_consumed == 74
    assert entry.real_cost_usd == Decimal("0.00148")


@pytest.mark.asyncio
async def test_phase3_actions_not_configured_throw_not_implemented() -> None:
    fake = FakeAiTransport()
    unconfigured = LocalizationAiSettings()
    client = _ai_client(fake, unconfigured)

    with pytest.raises(NotImplementedError, match="not configured"):
        await MtOptimizeService(client).optimize_async("r", "s", "de-DE")
    with pytest.raises(NotImplementedError, match="not configured"):
        await QpsScoringService(client).score_async("s", "t", "de-DE")
    with pytest.raises(NotImplementedError, match="not configured"):
        await AutoRoutingService(client).should_route_to_review_async(80, 70)

    assert fake.requests == []

    # A missing client is the same 501 path.
    with pytest.raises(NotImplementedError, match="not configured"):
        await MtOptimizeService().optimize_async("r", "s", "de-DE")
