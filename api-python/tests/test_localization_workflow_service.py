"""Translated from WorkflowServiceTests.cs."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.localization.localization_translation import LocalizationTranslation
from app.models.localization.service_agreement import ServiceAgreement
from app.models.localization.service_tiers import ServiceTiers
from app.models.localization.team_assignment import TeamAssignment
from app.models.localization.translation_job import TranslationJob
from app.models.localization.vendor import Vendor
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
    jobs,
    seed_project,
    workflow,
)


async def _seed_agreement(db: AsyncSession, project_id: int) -> None:
    now = datetime.now(UTC)
    vendor = Vendor(
        name="Team", alias="Vendor Team Test", languages="de-DE,fr-FR"
    )
    db.add(vendor)
    await db.flush()
    agreement = ServiceAgreement(
        project_id=project_id,
        tier=ServiceTiers.GOLD,
        valid_from=now - timedelta(days=1),
        created_at=now,
    )
    db.add(agreement)
    await db.flush()
    db.add_all(
        [
            TeamAssignment(
                agreement_id=agreement.id,
                vendor_id=vendor.id,
                locale_code="de-DE",
                member_count=6,
            ),
            TeamAssignment(
                agreement_id=agreement.id,
                vendor_id=vendor.id,
                locale_code="fr-FR",
                member_count=6,
            ),
        ]
    )
    await db.flush()


@pytest.mark.asyncio
async def test_create_translation_jobs_action_matches_direct_call(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    await _seed_agreement(db, seed.project.id)
    job_service = jobs(db)
    flow = workflow(db)

    direct = await job_service.create_job_async(seed.project.slug, "fr-FR")
    assert direct.string_count == 2
    assert direct.word_count == 4

    step = await flow.add_step_async(
        seed.project.slug,
        AddWorkflowStepRequest(action="Create Translation Jobs"),
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "1 jobs created, 1 skipped"

    via_workflow = (
        await db.execute(
            select(TranslationJob).where(TranslationJob.locale_code == "de-DE")
        )
    ).scalar_one()
    assert via_workflow.status == "Assigned"
    assert via_workflow.string_count == direct.string_count
    assert via_workflow.word_count == direct.word_count


@pytest.mark.asyncio
async def test_create_translation_jobs_action_skips_locales_with_nothing_left_to_translate(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    await _seed_agreement(db, seed.project.id)
    flow = workflow(db)

    for locale in ["de-DE", "fr-FR"]:
        for item in seed.strings:
            db.add(
                LocalizationTranslation(
                    string_id=item.id,
                    locale_code=locale,
                    target_text="done",
                    stage="Approved",
                    translation_source="Manual",
                    needs_review=False,
                    updated_at=datetime.now(UTC),
                )
            )
    await db.flush()

    step = await flow.add_step_async(
        seed.project.slug,
        AddWorkflowStepRequest(action="Create Translation Jobs"),
    )
    ran = await flow.run_step_async(seed.project.slug, step.id)

    assert ran.last_run_outcome == "0 jobs created, 2 skipped"
    created = (await db.execute(select(TranslationJob))).scalars().all()
    assert created == []


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
    db = scratch_session
    seed = await seed_project(db)
    # Production wiring: the real QpsScoringService stub, not the fake scorer.
    flow = WorkflowService(
        db,
        FakeTranslationProvider(),
        MtOptimizeService(),
        QpsScoringService(),
        AutoRoutingService(),
        jobs(db),
    )

    for action in ["Run MT Optimize", "Score Quality", "Auto-Route"]:
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
                    updated_at=datetime.now(UTC),
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
