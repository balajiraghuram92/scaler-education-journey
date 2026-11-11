"""Translated from BackfillReconciliationTests.cs.

Tests that need the full extracted seed data (java_vertical.json) are skipped until
tools/extract_seed_data.py has been run; the reconciliation and backfill logic itself
is covered with hand-built fixtures on the scratch database.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.course_module import CourseModule
from app.models.lesson import Lesson
from app.models.migration_reconciliation import MigrationReconciliation
from app.models.study_task import StudyTask
from app.models.study_task_content_link import StudyTaskContentLink
from app.models.study_vertical import StudyVertical
from app.services.reconciliation.fde_reconciler import FdeReconciler
from app.services.reconciliation.java_reconciler import JavaReconciler
from app.services.reconciliation.reconciliation_models import ReconciliationExecutionMode

DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "app",
    "seed",
    "data",
    "java_vertical.json",
)

needs_seed_data = pytest.mark.skipif(
    not os.path.isfile(DATA_PATH),
    reason="needs tools/extract_seed_data.py output (not run: shell unavailable)",
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _add_vertical(db: AsyncSession, name: str, vertical_id: int | None = None) -> StudyVertical:
    vertical = StudyVertical(name=name, description="d", updated_at=_now())
    if vertical_id is not None:
        vertical.id = vertical_id
    db.add(vertical)
    await db.flush()
    await db.refresh(vertical)
    return vertical


@pytest.mark.asyncio
@needs_seed_data
async def test_java_seeder_seeds_vertical_course_modules_lessons_and_tasks(
    scratch_session: AsyncSession,
) -> None:
    from app.seed.java_vertical_seed_data import seed as seed_java

    db = scratch_session
    await seed_java(db)

    vertical = (
        await db.execute(
            select(StudyVertical).where(StudyVertical.name == "Java & Spring Architecture")
        )
    ).scalar_one_or_none()
    assert vertical is not None
    task_count = (
        await db.execute(
            select(func.count(StudyTask.id)).where(StudyTask.vertical_id == vertical.id)
        )
    ).scalar_one()
    assert task_count == 28

    course = (
        await db.execute(select(Course).where(Course.slug == "java-spring-lld"))
    ).scalar_one_or_none()
    assert course is not None
    module_count = (
        await db.execute(
            select(func.count(CourseModule.id)).where(CourseModule.course_id == course.id)
        )
    ).scalar_one()
    assert module_count == 6
    lesson_total = (
        await db.execute(
            select(func.count(Lesson.id))
            .select_from(Lesson)
            .join(CourseModule, Lesson.module_id == CourseModule.id)
            .where(CourseModule.course_id == course.id)
        )
    ).scalar_one()
    assert lesson_total == 22


@pytest.mark.asyncio
async def test_phase2_backfill_replaces_only_needing_lessons_and_marks_draft(
    scratch_session: AsyncSession,
) -> None:
    from app.seed.java_vertical_seed_data import _backfill_lesson_content

    db = scratch_session
    now = _now()
    course = Course(
        slug="java-spring-lld", title="t", description="d", order_index=1,
        path_type="Course", is_published=True, created_at=now, updated_at=now,
    )
    db.add(course)
    await db.flush()
    module = CourseModule(
        course_id=course.id, slug="m", title="M", description="d", badge="M",
        order_index=1, created_at=now, updated_at=now,
    )
    db.add(module)
    await db.flush()
    authored_body = (
        "## Practical Backend Scenario\nX\n## Practice Loop\nY\n## Evidence of Understanding\nZ"
    )
    outline_body = "Short outline without required sections."
    preslugged_preserved = authored_body
    lessons = [
        Lesson(module_id=module.id, slug="outline-lesson", title="Outline Lesson",
               description="", lecture_number=1, class_date="", content_body=outline_body,
               estimated_minutes=10, is_completed=False, difficulty="Intermediate",
               created_at=now, updated_at=now),
        Lesson(module_id=module.id, slug="empty-lesson", title="Empty Lesson",
               description="", lecture_number=2, class_date="", content_body="",
               estimated_minutes=10, is_completed=False, difficulty="Intermediate",
               created_at=now, updated_at=now),
        Lesson(module_id=module.id, slug="complete-lesson", title="Complete Lesson",
               description="", lecture_number=3, class_date="", content_body=preslugged_preserved,
               estimated_minutes=10, is_completed=False, difficulty="Intermediate",
               created_at=now, updated_at=now),
    ]
    for lesson in lessons:
        db.add(lesson)
    await db.flush()

    authored = {"outline-lesson": authored_body, "empty-lesson": authored_body}
    await _backfill_lesson_content(db, course.id, authored)

    by_slug = {
        row.slug: row
        for row in (
            await db.execute(select(Lesson).where(Lesson.module_id == module.id))
        ).scalars().all()
    }
    assert by_slug["outline-lesson"].content_body == authored_body
    assert by_slug["outline-lesson"].content_status == "Draft"
    assert by_slug["empty-lesson"].content_body == authored_body
    assert by_slug["empty-lesson"].content_status == "Draft"
    assert by_slug["complete-lesson"].content_body == preslugged_preserved
    assert by_slug["complete-lesson"].content_status == "Published"


@pytest.mark.asyncio
@needs_seed_data
async def test_phase3a_apply_links_tasks_and_is_idempotent(scratch_session: AsyncSession) -> None:
    from app.seed.java_vertical_seed_data import seed as seed_java

    db = scratch_session
    await seed_java(db)
    reconciler = JavaReconciler(db)

    first = await reconciler.reconcile_java(ReconciliationExecutionMode.APPLY)

    assert first.verified_count == 27
    link_count = (await db.execute(select(func.count(StudyTaskContentLink.task_id)))).scalar_one()
    assert link_count == 27
    assert (
        await db.execute(select(func.count(StudyTask.id)))
    ).scalar_one() == 28
    assert (await db.execute(select(func.count(Course.id)))).scalar_one() >= 1

    second = await reconciler.reconcile_java(ReconciliationExecutionMode.APPLY)
    assert second.verified_count == 27
    assert (await db.execute(select(func.count(StudyTaskContentLink.task_id)))).scalar_one() == 27


@pytest.mark.asyncio
async def test_phase3a_repeat_apply_repairs_missing_links(scratch_session: AsyncSession) -> None:
    from app.services.reconciliation.java_reconciler import LEGACY_LESSON_SLUG_MAP

    db = scratch_session
    now = _now()
    vertical = await _add_vertical(db, "Java & Spring Architecture")
    titles = list(LEGACY_LESSON_SLUG_MAP)[:22]
    for title in titles:
        db.add(StudyTask(vertical_id=vertical.id, title=title, is_completed=False, module="M", updated_at=now))
    await db.flush()
    course = Course(
        slug="java-spring-lld", title="t", description="d", order_index=1,
        path_type="Course", is_published=True, created_at=now, updated_at=now,
    )
    db.add(course)
    await db.flush()
    module = CourseModule(
        course_id=course.id, slug="m", title="M", description="d", badge="M",
        order_index=1, created_at=now, updated_at=now,
    )
    db.add(module)
    await db.flush()
    for title in titles:
        db.add(
            Lesson(module_id=module.id, slug=LEGACY_LESSON_SLUG_MAP[title], title="t",
                   description="", lecture_number=1, class_date="", content_body="",
                   estimated_minutes=10, is_completed=False, difficulty="Intermediate",
                   created_at=now, updated_at=now)
        )
    await db.flush()

    reconciler = JavaReconciler(db)
    first = await reconciler.reconcile_java(ReconciliationExecutionMode.APPLY)
    assert first.verified_count == 22

    # Simulate drift: drop 5 links, then re-apply must restore all 22.
    links = (await db.execute(select(StudyTaskContentLink))).scalars().all()
    assert len(links) == 22
    for link in links[:5]:
        await db.delete(link)
    await db.flush()

    second = await reconciler.reconcile_java(ReconciliationExecutionMode.APPLY)
    assert second.verified_count == 22
    assert (await db.execute(select(func.count(StudyTaskContentLink.task_id)))).scalar_one() == 22


@pytest.mark.asyncio
async def test_fde_reconciler_resolves_vertical_candidates_deterministically(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    now = _now()
    await _add_vertical(db, "FDE Curriculum")
    await _add_vertical(db, "FDE Self-Study")
    reconciler = FdeReconciler(db)

    report = await reconciler.reconcile_fde(ReconciliationExecutionMode.DRY_RUN)

    assert report.scope == "fde"
    assert report.mode == ReconciliationExecutionMode.DRY_RUN
    assert report.discovered_count == 0
    assert report.conflict_count == 0


@pytest.mark.asyncio
async def test_fde_reconciler_unmapped_legacy_task_in_dry_run_without_side_effects(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    now = _now()
    vertical = await _add_vertical(db, "FDE Self-Study")
    db.add(StudyTask(vertical_id=vertical.id, title="Unmapped Legacy Task", is_completed=False, module="Module A", updated_at=now))
    await db.flush()
    reconciler = FdeReconciler(db)

    report = await reconciler.reconcile_fde(ReconciliationExecutionMode.DRY_RUN)

    assert report.proposed_count == 1
    assert report.mappings[0].mapping_status == "Proposed"
    assert report.mappings[0].issue_code == "UNMAPPED_LEGACY_TASK"
    assert (await db.execute(select(func.count(StudyTaskContentLink.task_id)))).scalar_one() == 0

    # On a real database (unlike EF InMemory), APPLY with a Proposed mapping fails:
    # the reconciler writes MigrationReconciliation.Status = "Proposed", which the
    # ck_migration_reconciliation_status check constraint rejects (Finding 13).
    with pytest.raises(IntegrityError):
        await reconciler.reconcile_fde(ReconciliationExecutionMode.APPLY)


@pytest.mark.asyncio
async def test_fde_reconciler_repeat_apply_run_is_idempotent(scratch_session: AsyncSession) -> None:
    db = scratch_session
    now = _now()
    vertical = await _add_vertical(db, "FDE Self-Study")
    task = StudyTask(vertical_id=vertical.id, title="Docker: Production Containers", is_completed=True, module="4. Cloud, DevOps, Kubernetes & Infrastructure", updated_at=now)
    db.add(task)
    await db.flush()
    course = Course(slug="fde-curriculum", title="t", description="d", order_index=1, path_type="Course", is_published=True, created_at=now, updated_at=now)
    db.add(course)
    await db.flush()
    module = CourseModule(course_id=course.id, slug="m", title="M", description="d", badge="M", order_index=1, created_at=now, updated_at=now)
    db.add(module)
    await db.flush()
    db.add(Lesson(module_id=module.id, slug="docker-production-containers", title="Docker: Production Containers", description="", lecture_number=1, class_date="", content_body="", estimated_minutes=10, is_completed=False, difficulty="Intermediate", created_at=now, updated_at=now))
    await db.flush()

    reconciler = FdeReconciler(db)
    first = await reconciler.reconcile_fde(ReconciliationExecutionMode.APPLY)
    assert first.verified_count == 1
    assert (await db.execute(select(func.count(StudyTaskContentLink.task_id)))).scalar_one() == 1
    assert (
        await db.execute(
            select(func.count(MigrationReconciliation.id)).where(
                MigrationReconciliation.migration_key == "PHASE-3B"
            )
        )
    ).scalar_one() == 1

    second = await reconciler.reconcile_fde(ReconciliationExecutionMode.APPLY)
    assert second.verified_count == 1
    assert (await db.execute(select(func.count(StudyTaskContentLink.task_id)))).scalar_one() == 1


@pytest.mark.asyncio
async def test_fde_reconciler_completion_mismatch_across_verticals_is_conflict(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    now = _now()
    curriculum = await _add_vertical(db, "FDE Curriculum")
    study = await _add_vertical(db, "FDE Self-Study")
    db.add(StudyTask(vertical_id=curriculum.id, title="Same Task", is_completed=True, module="M", updated_at=now))
    db.add(StudyTask(vertical_id=study.id, title="Same Task", is_completed=False, module="M", updated_at=now))
    await db.flush()
    reconciler = FdeReconciler(db)

    report = await reconciler.reconcile_fde(ReconciliationExecutionMode.DRY_RUN)

    assert report.conflict_count == 2
    assert {m.mapping_status for m in report.mappings} == {"Conflict"}
    assert {m.issue_code for m in report.mappings} == {"FDE_COMPLETION_MISMATCH"}
    assert {m.mapping_type for m in report.mappings} == {"DuplicateAlias"}


@pytest.mark.asyncio
async def test_fde_reconciler_without_canonical_targets_adds_no_entities(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    vertical = await _add_vertical(db, "FDE Self-Study")
    db.add(StudyTask(vertical_id=vertical.id, title="Lonely", is_completed=False, module="M", updated_at=_now()))
    await db.flush()
    reconciler = FdeReconciler(db)

    report = await reconciler.reconcile_fde(ReconciliationExecutionMode.DRY_RUN)

    assert report.proposed_count == 1
    assert (await db.execute(select(func.count(Course.id)))).scalar_one() == 0
    assert (await db.execute(select(func.count(StudyTaskContentLink.task_id)))).scalar_one() == 0
