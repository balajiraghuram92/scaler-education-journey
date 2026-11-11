"""Translated from JavaReconciliationTests.cs."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.course_module import CourseModule
from app.models.lesson import Lesson
from app.models.study_task import StudyTask
from app.models.study_vertical import StudyVertical
from app.services.reconciliation.fde_reconciler import FdeReconciler
from app.services.reconciliation.java_reconciler import JavaReconciler
from app.services.reconciliation.normalization_helper import (
    compute_sha256_checksum,
    generate_slug,
    normalize_text,
)
from app.services.reconciliation.reconciliation_models import ReconciliationExecutionMode


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def _add_vertical(db: AsyncSession, name: str) -> StudyVertical:
    vertical = StudyVertical(name=name, description="d", updated_at=_now())
    db.add(vertical)
    await db.flush()
    await db.refresh(vertical)
    return vertical


def test_normalization_helper_generates_canonical_keys() -> None:
    assert normalize_text("  Java   Basics: OOP Principles! ") == "java basics oop principles"
    assert generate_slug("Advanced Concurrency & Virtual Threads") == "advanced-concurrency-virtual-threads"

    checksum_a = compute_sha256_checksum("1|Module|Task Title|True")
    checksum_b = compute_sha256_checksum("1|Module|Task Title|True")
    assert checksum_a == checksum_b
    assert len(checksum_a) == 64


@pytest.mark.asyncio
async def test_java_reconciler_reviewed_legacy_title_matches_case_insensitively(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    now = _now()
    vertical = await _add_vertical(db, "Java & Spring Architecture")
    db.add(StudyTask(vertical_id=vertical.id, title="spring Boot 3 Core: inversion of control & dependency injection", is_completed=False, module="irrelevant", updated_at=now))
    await db.flush()
    course = Course(slug="java-spring-lld", title="t", description="d", order_index=1, path_type="Course", is_published=True, created_at=now, updated_at=now)
    db.add(course)
    await db.flush()
    module = CourseModule(course_id=course.id, slug="m", title="M", description="d", badge="M", order_index=1, created_at=now, updated_at=now)
    db.add(module)
    await db.flush()
    db.add(Lesson(module_id=module.id, slug="14-spring-boot-core", title="Spring Boot 3 Core", description="", lecture_number=1, class_date="", content_body="", estimated_minutes=10, is_completed=False, difficulty="Intermediate", created_at=now, updated_at=now))
    await db.flush()

    report = await JavaReconciler(db).reconcile_java(ReconciliationExecutionMode.DRY_RUN)

    assert report.scope == "java"
    assert report.discovered_count == 1
    assert report.verified_count == 1
    assert len(report.mappings) == 1
    assert report.mappings[0].legacy_title == "spring Boot 3 Core: inversion of control & dependency injection"


@pytest.mark.asyncio
async def test_java_reconciler_missing_vertical_reports_conflict_without_throwing(
    scratch_session: AsyncSession,
) -> None:
    report = await JavaReconciler(scratch_session).reconcile_java(
        ReconciliationExecutionMode.DRY_RUN
    )

    assert report.conflict_count == 1
    assert report.discovered_count == 0
    assert any("Java & Spring Architecture" in entry for entry in report.audit_log)


@pytest.mark.asyncio
async def test_fde_vertical_matching_is_strict_and_case_insensitive(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    await _add_vertical(db, "fde curriculum")
    await _add_vertical(db, "FDE SELF-STUDY ")

    report = await FdeReconciler(db).reconcile_fde(ReconciliationExecutionMode.DRY_RUN)

    assert report.conflict_count == 0
    assert report.discovered_count == 0
    assert any("Discovered 0 total FDE legacy tasks" in entry for entry in report.audit_log)
