"""Translated from WorkflowServiceTests.cs."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.localization.localization_translation import LocalizationTranslation
from app.models.localization.marketplace_job import MarketplaceJob
from app.models.localization.workflow_step import WorkflowStep
from app.schemas.localization_dtos import (
    AddWorkflowStepRequest,
    UpdateWorkflowStepRequest,
)
from app.services.localization.auto_routing_service import AutoRoutingService
from app.services.localization.mt_optimize_service import MtOptimizeService
from app.services.localization.qps_scoring_service import QpsScoringService
from app.services.localization.workflow_service import WorkflowService

from .localization_fixture import (
    FakeTranslationProvider,
    marketplace,
    seed_project,
    workflow,
)


@pytest.mark.asyncio
async def test_post_to_marketplace_action_matches_direct_call(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)
    flow = workflow(db)

    direct = await market.post_to_marketplace_async(seed.project.slug, "fr-FR")
    assert direct.string_count == 2
    assert direct.word_count == 4

    step = await flow.add_step_async(
        seed.project.slug,
        AddWorkflowStepRequest(action="Post to Marketplace"),
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "1 marketplace jobs posted, 1 skipped"

    via_workflow = (
        await db.execute(
            select(MarketplaceJob).where(MarketplaceJob.locale_code == "de-DE")
        )
    ).scalar_one()
    assert via_workflow.status == "Open"
    assert via_workflow.string_count == direct.string_count
    assert via_workflow.word_count == direct.word_count
    assert via_workflow.suggested_price_low == direct.suggested_price_low
    assert via_workflow.suggested_price_high == direct.suggested_price_high


@pytest.mark.asyncio
async def test_post_to_marketplace_action_skips_locales_with_nothing_left_to_translate(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    flow = workflow(db)

    for locale in ["de-DE", "fr-FR"]:
        for item in seed.strings:
            db.add(
                LocalizationTranslation(
                    string_id=item.id,
                    locale_code=locale,
                    target_text="done",
                    stage="Translated",
                    translation_source="Manual",
                    needs_review=False,
                    updated_at=datetime.now(timezone.utc),
                )
            )
    await db.flush()

    step = await flow.add_step_async(
        seed.project.slug,
        AddWorkflowStepRequest(action="Post to Marketplace"),
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "0 marketplace jobs posted, 2 skipped"
    jobs = (await db.execute(select(MarketplaceJob))).scalars().all()
    assert jobs == []


@pytest.mark.asyncio
async def test_add_step_unknown_action_is_rejected(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    flow = workflow(db)

    with pytest.raises(ValueError):
        await flow.add_step_async(
            seed.project.slug, AddWorkflowStepRequest(action="Teleport")
        )

    steps = (await db.execute(select(WorkflowStep))).scalars().all()
    assert steps == []


@pytest.mark.asyncio
async def test_update_step_unknown_trigger_is_rejected(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    flow = workflow(db)

    step = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Mark Translated")
    )

    with pytest.raises(ValueError):
        await flow.update_step_async(
            seed.project.slug,
            step.id,
            UpdateWorkflowStepRequest(
                trigger="On Full Moon", action="Mark Translated"
            ),
        )


@pytest.mark.asyncio
async def test_run_step_unknown_action_throws_invalid_operation_exception(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    flow = workflow(db)

    # Bypass AddStepAsync validation to simulate a row written before validation existed.
    legacy = WorkflowStep(
        project_id=seed.project.id,
        order=1,
        trigger="On Manual Click",
        action="Legacy Mystery Action",
    )
    db.add(legacy)
    await db.flush()

    with pytest.raises(RuntimeError):
        await flow.run_step_async(seed.project.slug, legacy.id)


@pytest.mark.asyncio
async def test_run_step_phase3_actions_still_surface_not_implemented(
    scratch_session: AsyncSession,
) -> None:
    # NOTE (Finding: stale pre-LA4 expectation): translated verbatim. Post-LA4
    # the AI call happens only per-string, so on this translation-less project
    # the actions return "0 strings ..." instead of throwing; this test fails
    # against post-LA4 behavior in both stacks. The 501 path is covered by
    # test_phase3_actions_not_configured_throw_not_implemented instead.
    db = scratch_session
    seed = await seed_project(db)
    # Production wiring: the real QpsScoringService stub, not the fake scorer.
    flow = WorkflowService(
        db,
        FakeTranslationProvider(),
        MtOptimizeService(),
        QpsScoringService(),
        AutoRoutingService(),
        marketplace(db),
    )

    for action in ["Run MT Optimize", "Score QPS", "Auto-Route"]:
        step = await flow.add_step_async(
            seed.project.slug, AddWorkflowStepRequest(action=action)
        )
        with pytest.raises(NotImplementedError):
            await flow.run_step_async(seed.project.slug, step.id)


@pytest.mark.asyncio
async def test_run_step_mark_translated_send_to_review_approve_chain(
    scratch_session: AsyncSession,
) -> None:
    # Exercises the three Phase 1 bulk actions end to end (no C# equivalent;
    # the C# suite only covers them indirectly through seeded last-run lines).
    db = scratch_session
    seed = await seed_project(db)
    flow = workflow(db)

    for locale in ["de-DE", "fr-FR"]:
        for item in seed.strings:
            db.add(
                LocalizationTranslation(
                    string_id=item.id,
                    locale_code=locale,
                    target_text="text",
                    stage="New",
                    translation_source="Manual",
                    needs_review=False,
                    updated_at=datetime.now(timezone.utc),
                )
            )
    await db.flush()

    mark = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Mark Translated")
    )
    ran_mark = await flow.run_step_async(seed.project.slug, mark.id)
    assert ran_mark.last_run_outcome == "4 strings affected"

    review = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Send to Review")
    )
    ran_review = await flow.run_step_async(seed.project.slug, review.id)
    assert ran_review.last_run_outcome == "4 strings affected"

    approve = await flow.add_step_async(
        seed.project.slug, AddWorkflowStepRequest(action="Approve")
    )
    ran_approve = await flow.run_step_async(seed.project.slug, approve.id)
    assert ran_approve.last_run_outcome == "4 strings affected"

    stages = (
        await db.execute(select(LocalizationTranslation.stage))
    ).scalars().all()
    assert stages == ["Approved"] * 4
    assert ran_approve.last_run_at is not None
