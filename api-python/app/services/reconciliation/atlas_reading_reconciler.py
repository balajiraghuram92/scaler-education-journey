"""Ported from api/Services/Reconciliation/AtlasReadingReconciler.cs."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.knowledge_concept import KnowledgeConcept
from ...models.knowledge_thread import KnowledgeThread
from ...models.knowledge_thread_step import KnowledgeThreadStep
from ...models.lesson import Lesson
from ...models.reading_map_item import ReadingMapItem
from .normalization_helper import normalize_text
from .reconciliation_models import (
    ReconciliationExecutionMode,
    ReconciliationReport,
)

logger = logging.getLogger(__name__)


class AtlasReadingReconciler:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _utcnow(self) -> datetime:
        return datetime.now(timezone.utc)

    async def reconcile_atlas_and_reading(
        self, mode: ReconciliationExecutionMode
    ) -> ReconciliationReport:
        report = ReconciliationReport(
            scope="atlas-reading", mode=mode, executed_at=self._utcnow()
        )

        reading_items = (
            await self._session.execute(select(ReadingMapItem))
        ).scalars().all()
        threads = (
            await self._session.execute(
                select(KnowledgeThread).options(selectinload(KnowledgeThread.steps))
            )
        ).scalars().all()
        concepts = (
            await self._session.execute(select(KnowledgeConcept))
        ).scalars().all()
        lessons = (await self._session.execute(select(Lesson))).scalars().all()

        report.discovered_count = len(reading_items) + len(threads)

        if mode == ReconciliationExecutionMode.APPLY:
            try:
                # 1. Tag prototype reading map items as IsSeeded = true
                for item in reading_items:
                    item.is_seeded = True
                    # Attempt linking with Java lessons
                    normalized_title = normalize_text(item.title)
                    matched_lesson = next(
                        (
                            lesson
                            for lesson in lessons
                            if normalize_text(lesson.title) == normalized_title
                            or normalized_title in normalize_text(lesson.title)
                        ),
                        None,
                    )
                    if matched_lesson is not None:
                        item.lesson_id = matched_lesson.id

                # 2. Normalize KnowledgeThread.RawPath into KnowledgeThreadStep
                for thread in threads:
                    if not thread.raw_path or not thread.raw_path.strip():
                        continue

                    # Parse path items separated by "→" or "->"
                    segments = _split_path(thread.raw_path)
                    step_idx = 0
                    for segment in segments:
                        normalized_segment = normalize_text(segment)
                        matched_concept = next(
                            (
                                concept
                                for concept in concepts
                                if normalize_text(concept.title) == normalized_segment
                                or normalize_text(concept.slug) == normalized_segment
                            ),
                            None,
                        )
                        existing_step = await self._session.get(
                            KnowledgeThreadStep, (thread.id, step_idx)
                        )
                        if existing_step is None:
                            self._session.add(
                                KnowledgeThreadStep(
                                    thread_id=thread.id,
                                    order_index=step_idx,
                                    label=segment,
                                    concept_id=matched_concept.id
                                    if matched_concept is not None
                                    else None,
                                    created_at=self._utcnow(),
                                )
                            )
                        step_idx += 1

                await self._session.flush()
                report.audit_log.append(
                    "Reading map seed tagging and Knowledge thread step normalization completed."
                )
            except Exception as exc:
                await self._session.rollback()
                report.audit_log.append(f"ERROR: Atlas/Reading transaction failed: {exc}")
                raise

        return report


def split_thread_path(raw_path: str) -> list[str]:
    """Split on "→", "->" or ">", dropping empties and trimming (C# Split semantics)."""
    return _split_path(raw_path)


def _split_path(raw_path: str) -> list[str]:
    # C# tries separators in order ["→", "->", ">"] at each position; a "->"
    # consumes both chars so the ">" alternative never splits it.
    segments: list[str] = []
    current: list[str] = []
    i = 0
    while i < len(raw_path):
        if raw_path[i] == "→":
            segments.append("".join(current))
            current = []
            i += 1
        elif raw_path.startswith("->", i):
            segments.append("".join(current))
            current = []
            i += 2
        elif raw_path[i] == ">":
            segments.append("".join(current))
            current = []
            i += 1
        else:
            current.append(raw_path[i])
            i += 1
    segments.append("".join(current))
    return [s.strip() for s in segments if s.strip()]
