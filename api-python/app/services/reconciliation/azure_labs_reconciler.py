"""Ported from api/Services/Reconciliation/AzureLabsReconciler.cs."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.course import Course
from ...models.course_module import CourseModule
from ...models.lesson import Lesson
from ...models.migration_reconciliation import MigrationReconciliation
from ...models.problem import Problem
from ...models.study_task import StudyTask
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


class AzureLabsReconciler:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _utcnow(self) -> datetime:
        return datetime.now(timezone.utc)

    async def reconcile_azure_and_labs(
        self, mode: ReconciliationExecutionMode
    ) -> ReconciliationReport:
        report = ReconciliationReport(
            scope="azure-labs", mode=mode, executed_at=self._utcnow()
        )

        # 1. Strict Vertical Lookups with normalized exact matching (No numeric IDs, Contains, or FirstOrDefault)
        all_verticals = (
            await self._session.execute(
                select(StudyVertical).options(selectinload(StudyVertical.tasks))
            )
        ).scalars().all()

        azure_normalized = normalize_text("Azure Certifications")
        azure_candidates = [
            v for v in all_verticals if normalize_text(v.name) == azure_normalized
        ]
        labs_normalized = normalize_text("Lab Projects")
        labs_candidates = [
            v for v in all_verticals if normalize_text(v.name) == labs_normalized
        ]

        azure_vertical = None
        if not azure_candidates:
            report.conflict_count += 1
            report.audit_log.append(
                "Missing source conflict: Required source vertical 'Azure Certifications' was not found."
            )
        elif len(azure_candidates) > 1:
            report.conflict_count += 1
            details = ", ".join(
                f"[Id: {c.id}, Name: '{c.name}']" for c in azure_candidates
            )
            report.audit_log.append(
                f"Ambiguity conflict: Expected exactly 1 vertical for 'Azure Certifications', found {len(azure_candidates)} candidates: {details}."
            )
        else:
            azure_vertical = azure_candidates[0]

        labs_vertical = None
        if not labs_candidates:
            report.conflict_count += 1
            report.audit_log.append(
                "Missing source conflict: Required source vertical 'Lab Projects' was not found."
            )
        elif len(labs_candidates) > 1:
            report.conflict_count += 1
            details = ", ".join(
                f"[Id: {c.id}, Name: '{c.name}']" for c in labs_candidates
            )
            report.audit_log.append(
                f"Ambiguity conflict: Expected exactly 1 vertical for 'Lab Projects', found {len(labs_candidates)} candidates: {details}."
            )
        else:
            labs_vertical = labs_candidates[0]

        if azure_vertical is None or labs_vertical is None:
            report.audit_log.append(
                "Reconciliation stopped: One or more required Azure/Labs source verticals could not be uniquely resolved."
            )
            return report

        # 2. Fetch pre-existing canonical Courses, Modules, Lessons, Problems (Do not fabricate new ones)
        azure_course_candidates = (
            await self._session.execute(
                select(Course)
                .options(
                    selectinload(Course.modules)
                    .selectinload(CourseModule.lessons)
                    .selectinload(Lesson.problems)
                )
                .where(Course.slug == "azure-certification")
            )
        ).scalars().all()
        all_azure_lessons = (
            [l for m in azure_course_candidates[0].modules for l in m.lessons]
            if len(azure_course_candidates) == 1
            else []
        )
        all_azure_problems = [p for l in all_azure_lessons for p in l.problems]

        labs_course_candidates = (
            await self._session.execute(
                select(Course)
                .options(
                    selectinload(Course.modules)
                    .selectinload(CourseModule.lessons)
                    .selectinload(Lesson.problems)
                )
                .where(Course.slug == "lab-projects")
            )
        ).scalars().all()
        all_labs_lessons = (
            [l for m in labs_course_candidates[0].modules for l in m.lessons]
            if len(labs_course_candidates) == 1
            else []
        )
        all_labs_problems = [p for l in all_labs_lessons for p in l.problems]

        report.discovered_count = len(azure_vertical.tasks) + len(labs_vertical.tasks)

        # 3. Classify Azure Tasks against pre-existing canonical Azure lessons/problems
        for task in azure_vertical.tasks:
            report.mappings.append(
                self._classify(
                    report,
                    task,
                    all_azure_problems,
                    all_azure_lessons,
                    "No pre-existing canonical Azure lesson found in curriculum. Retained as proposed item without fabricating database entities.",
                )
            )

        # 4. Classify Lab Tasks against pre-existing canonical Lab lessons/problems
        for task in labs_vertical.tasks:
            report.mappings.append(
                self._classify(
                    report,
                    task,
                    all_labs_problems,
                    all_labs_lessons,
                    "No pre-existing canonical Lab lesson found in curriculum. Retained as proposed item without fabricating database entities.",
                )
            )

        # 5. Apply mode creates StudyTaskContentLink ONLY for Verified mappings and audits in MigrationReconciliation
        if mode == ReconciliationExecutionMode.APPLY:
            try:
                for candidate in report.mappings:
                    # Create or update StudyTaskContentLink ONLY for Verified mappings
                    if candidate.mapping_status == "Verified":
                        link = await self._session.get(
                            StudyTaskContentLink, candidate.legacy_task_id
                        )
                        now = self._utcnow()
                        if link is None:
                            self._session.add(
                                StudyTaskContentLink(
                                    task_id=candidate.legacy_task_id,
                                    lesson_id=candidate.target_lesson_id,
                                    problem_id=candidate.target_problem_id,
                                    mapping_type=candidate.mapping_type,
                                    mapping_status="Verified",
                                    confidence=candidate.confidence,
                                    source_checksum=candidate.source_checksum,
                                    verified_at=now,
                                    created_at=now,
                                    updated_at=now,
                                )
                            )
                        else:
                            link.lesson_id = candidate.target_lesson_id
                            link.problem_id = candidate.target_problem_id
                            link.mapping_type = candidate.mapping_type
                            link.mapping_status = "Verified"
                            link.confidence = candidate.confidence
                            link.source_checksum = candidate.source_checksum
                            link.verified_at = link.verified_at or now
                            link.updated_at = now

                    # Audit records in MigrationReconciliation (Idempotent)
                    rec = (
                        await self._session.execute(
                            select(MigrationReconciliation).where(
                                MigrationReconciliation.migration_key == "PHASE-3C",
                                MigrationReconciliation.source_type == "StudyTask",
                                MigrationReconciliation.source_id
                                == str(candidate.legacy_task_id),
                            )
                        )
                    ).scalar_one_or_none()
                    target_type = (
                        "Lesson"
                        if candidate.target_lesson_id is not None
                        else ("Problem" if candidate.target_problem_id is not None else None)
                    )
                    target_id = candidate.target_lesson_id
                    if target_id is None:
                        target_id = candidate.target_problem_id
                    status = (
                        "Applied"
                        if candidate.mapping_status == "Verified"
                        else candidate.mapping_status
                    )
                    now = self._utcnow()
                    if rec is None:
                        self._session.add(
                            MigrationReconciliation(
                                migration_key="PHASE-3C",
                                source_type="StudyTask",
                                source_id=str(candidate.legacy_task_id),
                                target_type=target_type,
                                target_id=str(target_id) if target_id is not None else None,
                                source_checksum=candidate.source_checksum,
                                status=status,
                                issue_code=candidate.issue_code,
                                details_json=candidate.to_details_json(),
                                applied_at=now,
                                updated_at=now,
                            )
                        )
                    else:
                        rec.target_type = target_type
                        rec.target_id = str(target_id) if target_id is not None else None
                        rec.status = status
                        rec.issue_code = candidate.issue_code
                        rec.details_json = candidate.to_details_json()
                        rec.updated_at = now

                await self._session.flush()
                report.audit_log.append(
                    "Azure & Labs reconciliation changes committed successfully without fabricating database entities."
                )
            except Exception as exc:
                await self._session.rollback()
                report.audit_log.append(f"ERROR: Azure/Labs transaction failed: {exc}")
                raise

        return report

    def _classify(
        self,
        report: ReconciliationReport,
        task: StudyTask,
        problems: list[Problem],
        lessons: list[Lesson],
        unmapped_note: str,
    ) -> MappingCandidate:
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
        matching_problems = [
            p for p in problems if normalize_text(p.title) == normalized_title
        ]
        matching_lessons = [
            les for les in lessons if normalize_text(les.title) == normalized_title
        ]
        total_matches = len(matching_problems) + len(matching_lessons)
        if total_matches == 0:
            candidate.mapping_type = "Manual"
            candidate.mapping_status = "Proposed"
            candidate.confidence = Decimal("0.6000")
            candidate.issue_code = "UNMAPPED_LEGACY_TASK"
            candidate.note = unmapped_note
            report.proposed_count += 1
        elif total_matches > 1:
            candidate.mapping_type = "Ambiguous"
            candidate.mapping_status = "Conflict"
            candidate.confidence = Decimal("0.5000")
            candidate.issue_code = "AMBIGUOUS_CANONICAL_TARGET"
            candidate.note = (
                f"Ambiguous target match: found {len(matching_lessons)} lessons "
                f"and {len(matching_problems)} problems matching title '{task.title}'."
            )
            report.conflict_count += 1
        elif len(matching_problems) == 1:
            problem = matching_problems[0]
            candidate.target_problem_id = problem.id
            candidate.target_title = problem.title
            candidate.mapping_type = "Exact"
            candidate.mapping_status = "Verified"
            candidate.confidence = Decimal("1.0000")
            candidate.note = f"Deterministically mapped to canonical Problem (Id: {problem.id})."
            report.exact_mapped_count += 1
            report.verified_count += 1
        else:  # matchingLessons.Count == 1
            lesson = matching_lessons[0]
            candidate.target_lesson_id = lesson.id
            candidate.target_title = lesson.title
            candidate.mapping_type = "TitleAndModule"
            candidate.mapping_status = "Verified"
            candidate.confidence = Decimal("0.9500")
            candidate.note = f"Deterministically mapped to canonical Lesson (Id: {lesson.id})."
            report.exact_mapped_count += 1
            report.verified_count += 1
        return candidate
