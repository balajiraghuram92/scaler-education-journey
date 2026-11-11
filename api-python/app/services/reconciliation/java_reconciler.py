"""Ported from api/Services/Reconciliation/JavaReconciler.cs."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.course import Course
from ...models.course_domain_link import CourseDomainLink
from ...models.course_module import CourseModule
from ...models.knowledge_domain import KnowledgeDomain
from ...models.lesson import Lesson
from ...models.migration_reconciliation import MigrationReconciliation
from ...models.study_task_content_link import StudyTaskContentLink
from ...models.study_vertical import StudyVertical
from .normalization_helper import (
    compute_sha256_checksum,
    normalize_text,
)
from .reconciliation_models import (
    MappingCandidate,
    ReconciliationExecutionMode,
    ReconciliationReport,
)

logger = logging.getLogger(__name__)

# The legacy tracker used a different editorial title format from the canonical
# course. These are reviewed, deterministic title-to-slug mappings; they avoid
# fuzzy matching and keep progress synchronization safe.
LEGACY_LESSON_SLUG_MAP = {
    "Lesson 01: Intro to LLD for Scalable & AI-Ready Systems": "01-intro-to-lld",
    "Lesson 02: OOP-1 Intro Lab (Core OOP Foundations)": "02-oop-1-intro-lab",
    "Lesson 03: OOP-2 Access Modifiers, Encapsulation & Inheritance": "03-oop-2-access-modifiers-encapsulation",
    "Lesson 04: OOP-3 Polymorphism, Interfaces & Abstract Classes": "04-oop-3-polymorphism-interfaces",
    "Lesson 05: OOP-4 Library Management System (LMS) Lab": "05-oop-4-lms-lab",
    "Lesson 06: Concurrency 1: Processes, Threads & PCB Context Switching": "06-concurrency-1-threads",
    "Lesson 07: Concurrency 2: Executors, Thread Pools & Callable/Future": "07-concurrency-2-executors",
    "Lesson 08: Concurrency 3: Synchronization, Race Conditions & Locks": "08-concurrency-3-synchronization",
    "Lesson 09: Concurrency 4: Semaphores & Bounded Buffer": "09-concurrency-4-semaphores",
    "Lesson 10: Java Advanced 1: Generics, Wildcards & Type Erasure": "10-java-adv-1-generics",
    "Lesson 11: Java Advanced 2: Collections Lab & Comparator/Comparable": "11-java-adv-2-collections-lab",
    "Lesson 12: Java Advanced 3: Lambdas, Functional Interfaces & Streams": "12-java-adv-3-lambdas-streams",
    "Lesson 13: Java Advanced 4: Streams in Depth & Exception Architecture": "13-java-adv-4-streams-exceptions",
    "Spring Boot 3 Core: Inversion of Control & Dependency Injection": "14-spring-boot-core",
    "Data Layer: Spring Data JPA, Hibernate & PostgreSQL 16": "15-spring-data-jpa",
    "API Architecture: RESTful Services, Validation & Security": "16-spring-rest-api",
    "Contest Capstone: Java, OOP & Concurrency Machine Coding": "17-machine-coding-capstone",
}

LEGACY_PROBLEM_SLUG_MAP = {
    "OOP-2 Problem 1: Immutable Fare (Warm-up)": "prb1-immutable-fare",
    "OOP-2 Problem 2: Driver Onboarding (Easy-Mid)": "prb2-driver-onboarding",
    "OOP-2 Problem 3: Vehicle Hierarchy (Mid)": "prb3-vehicle-hierarchy",
    "OOP-2 Problem 4: Trip Copy Semantics (Mid-Hard)": "prb4-trip-copy-semantics",
    "OOP-2 Problem 5: The equals/hashCode Contract (Hard)": "prb5-equals-hashcode-contract",
}


class JavaReconciler:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _utcnow(self) -> datetime:
        return datetime.now(timezone.utc)

    async def reconcile_java(self, mode: ReconciliationExecutionMode) -> ReconciliationReport:
        report = ReconciliationReport(scope="java", mode=mode, executed_at=self._utcnow())
        report.audit_log.append(f"Starting Java reconciliation in {mode.value} mode.")

        # 1. Fetch Java Vertical by canonical normalized exact name (No numeric IDs, Contains, or FirstOrDefault)
        all_verticals = (
            await self._session.execute(
                select(StudyVertical).options(selectinload(StudyVertical.tasks))
            )
        ).scalars().all()
        java_normalized = normalize_text("Java & Spring Architecture")
        java_candidates = [v for v in all_verticals if normalize_text(v.name) == java_normalized]

        if not java_candidates:
            report.conflict_count += 1
            report.audit_log.append(
                "Missing source conflict: Required source vertical 'Java & Spring Architecture' was not found."
            )
            return report
        if len(java_candidates) > 1:
            report.conflict_count += 1
            details = ", ".join(f"[Id: {c.id}, Name: '{c.name}']" for c in java_candidates)
            report.audit_log.append(
                f"Ambiguity conflict: Expected exactly 1 vertical for 'Java & Spring Architecture', found {len(java_candidates)} candidates: {details}."
            )
            return report
        java_vertical = java_candidates[0]

        report.audit_log.append(
            f"Found Java vertical '{java_vertical.name}' (Id: {java_vertical.id}) with {len(java_vertical.tasks)} legacy tasks."
        )
        report.discovered_count = len(java_vertical.tasks)

        # 2. Fetch Java Course, Modules, Lessons, Problems
        course_candidates = (
            await self._session.execute(
                select(Course)
                .options(
                    selectinload(Course.modules)
                    .selectinload(CourseModule.lessons)
                    .selectinload(Lesson.problems)
                )
                .where(Course.slug == "java-spring-lld")
            )
        ).scalars().all()
        if len(course_candidates) != 1:
            report.conflict_count += 1
            msg = (
                "Missing course conflict: Canonical Java Course 'java-spring-lld' not found in database."
                if not course_candidates
                else f"Ambiguity conflict: Expected 1 Java Course 'java-spring-lld', found {len(course_candidates)}."
            )
            report.audit_log.append(msg)
            return report

        java_course = course_candidates[0]
        all_lessons = [l for m in java_course.modules for l in m.lessons]
        all_problems = [p for l in all_lessons for p in l.problems]

        # 3. Classify and map legacy tasks
        for task in sorted(java_vertical.tasks, key=lambda t: t.id):
            # C# interpolates bools as "True"/"False"; Python str() matches that.
            raw_signature = f"{task.id}|{task.module}|{task.title}|{task.is_completed}"
            checksum = compute_sha256_checksum(raw_signature)
            normalized_title = normalize_text(task.title)

            candidate = MappingCandidate(
                legacy_task_id=task.id,
                legacy_title=task.title,
                legacy_module=task.module,
                legacy_is_completed=task.is_completed,
                source_checksum=checksum,
            )

            # Prefer the explicit reviewed mapping because the legacy tracker and
            # canonical course intentionally use different editorial titles.
            if task.title in LEGACY_PROBLEM_SLUG_MAP:
                matching_problems = [
                    p for p in all_problems if p.slug == LEGACY_PROBLEM_SLUG_MAP[task.title]
                ]
            else:
                matching_problems = [
                    p for p in all_problems if normalize_text(p.title) == normalized_title
                ]

            if len(matching_problems) == 1:
                matched = matching_problems[0]
                candidate.target_problem_id = matched.id
                candidate.target_title = matched.title
                candidate.mapping_type = "Exact"
                candidate.mapping_status = "Verified"
                candidate.confidence = Decimal("1.0000")
                candidate.note = f"Mapped to Problem {matched.id}"
                report.exact_mapped_count += 1
                report.verified_count += 1
            elif len(matching_problems) > 1:
                candidate.mapping_type = "Exact"
                candidate.mapping_status = "Conflict"
                candidate.confidence = Decimal("0.5000")
                candidate.issue_code = "AMBIGUOUS_PROBLEM_MATCH"
                candidate.note = f"Ambiguous problem match ({len(matching_problems)} matches)"
                report.conflict_count += 1
            else:
                if task.title in LEGACY_LESSON_SLUG_MAP:
                    matching_lessons = [
                        les
                        for les in all_lessons
                        if les.slug == LEGACY_LESSON_SLUG_MAP[task.title]
                    ]
                else:
                    matching_lessons = [
                        les
                        for les in all_lessons
                        if normalize_text(les.title) == normalized_title
                    ]
                if len(matching_lessons) == 1:
                    matched_lesson = matching_lessons[0]
                    candidate.target_lesson_id = matched_lesson.id
                    candidate.target_title = matched_lesson.title
                    candidate.mapping_type = "TitleAndModule"
                    candidate.mapping_status = "Verified"
                    candidate.confidence = Decimal("0.9500")
                    candidate.note = f"Mapped to Lesson {matched_lesson.id}"
                    report.exact_mapped_count += 1
                    report.verified_count += 1
                elif len(matching_lessons) > 1:
                    candidate.mapping_type = "TitleAndModule"
                    candidate.mapping_status = "Conflict"
                    candidate.confidence = Decimal("0.5000")
                    candidate.issue_code = "AMBIGUOUS_LESSON_MATCH"
                    candidate.note = f"Ambiguous lesson match ({len(matching_lessons)} matches)"
                    report.conflict_count += 1
                else:
                    # Spring / Capstone Outline candidates
                    candidate.mapping_type = "Manual"
                    candidate.mapping_status = "Proposed"
                    candidate.confidence = Decimal("0.7000")
                    candidate.note = "Spring/Capstone item - candidate for Outline lesson creation"
                    report.proposed_count += 1

            report.mappings.append(candidate)

        # 4. Apply Changes if Mode == Apply
        if mode == ReconciliationExecutionMode.APPLY:
            try:
                for candidate in [m for m in report.mappings if m.mapping_status == "Verified"]:
                    existing_link = await self._session.get(
                        StudyTaskContentLink, candidate.legacy_task_id
                    )
                    now = self._utcnow()
                    if existing_link is None:
                        self._session.add(
                            StudyTaskContentLink(
                                task_id=candidate.legacy_task_id,
                                lesson_id=candidate.target_lesson_id,
                                problem_id=candidate.target_problem_id,
                                mapping_type=candidate.mapping_type,
                                mapping_status=candidate.mapping_status,
                                confidence=candidate.confidence,
                                source_checksum=candidate.source_checksum,
                                verified_at=now,
                                created_at=now,
                                updated_at=now,
                            )
                        )
                    else:
                        existing_link.lesson_id = candidate.target_lesson_id
                        existing_link.problem_id = candidate.target_problem_id
                        existing_link.mapping_type = candidate.mapping_type
                        existing_link.mapping_status = candidate.mapping_status
                        existing_link.confidence = candidate.confidence
                        existing_link.source_checksum = candidate.source_checksum
                        existing_link.verified_at = now
                        existing_link.updated_at = now

                    # Record MigrationReconciliation entry
                    reconciliation_record = (
                        await self._session.execute(
                            select(MigrationReconciliation).where(
                                MigrationReconciliation.migration_key == "PHASE-3A",
                                MigrationReconciliation.source_type == "StudyTask",
                                MigrationReconciliation.source_id == str(candidate.legacy_task_id),
                            )
                        )
                    ).scalar_one_or_none()
                    target_type = "Lesson" if candidate.target_lesson_id is not None else "Problem"
                    target_id = candidate.target_lesson_id
                    if target_id is None:
                        target_id = candidate.target_problem_id
                    now = self._utcnow()
                    if reconciliation_record is None:
                        self._session.add(
                            MigrationReconciliation(
                                migration_key="PHASE-3A",
                                source_type="StudyTask",
                                source_id=str(candidate.legacy_task_id),
                                target_type=target_type,
                                target_id=str(target_id) if target_id is not None else None,
                                source_checksum=candidate.source_checksum,
                                status="Applied",
                                details_json=candidate.to_details_json(),
                                applied_at=now,
                                updated_at=now,
                            )
                        )
                    else:
                        reconciliation_record.status = "Applied"
                        reconciliation_record.target_type = target_type
                        reconciliation_record.target_id = (
                            str(target_id) if target_id is not None else None
                        )
                        reconciliation_record.details_json = candidate.to_details_json()
                        reconciliation_record.updated_at = now

                # Add CourseDomainLinks for Java: Foundations, Backend, Reliability
                domains = (
                    await self._session.execute(
                        select(KnowledgeDomain).where(
                            KnowledgeDomain.slug.in_(["foundations", "backend", "reliability"])
                            | KnowledgeDomain.code.in_(["FOUND", "BE", "SRE"])
                        )
                    )
                ).scalars().all()
                order_idx = 0
                for domain in domains:
                    existing_domain_link = await self._session.get(
                        CourseDomainLink, (java_course.id, domain.id)
                    )
                    if existing_domain_link is None:
                        self._session.add(
                            CourseDomainLink(
                                course_id=java_course.id,
                                domain_id=domain.id,
                                is_primary=domain.slug == "backend" or domain.code == "BE",
                                order_index=order_idx,
                                created_at=self._utcnow(),
                            )
                        )
                        order_idx += 1

                await self._session.flush()
                report.audit_log.append(
                    "Reconciliation changes committed successfully to database."
                )
            except Exception as exc:
                await self._session.rollback()
                report.audit_log.append(
                    f"ERROR: Reconciliation transaction rolled back due to error: {exc}"
                )
                raise

        return report
