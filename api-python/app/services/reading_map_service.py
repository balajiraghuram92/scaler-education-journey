"""Ported from api/Services/ReadingMapService.cs."""

from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.knowledge_thread import KnowledgeThread
from ..models.knowledge_thread_step import KnowledgeThreadStep
from ..models.learning_activity import LearningActivity
from ..models.reading_map_item import ReadingMapItem
from ..schemas.base import format_dotnet_datetime


class ReadingMapService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_reading_map(self) -> dict:
        items = (
            await self._session.execute(
                select(ReadingMapItem)
                .options(selectinload(ReadingMapItem.lesson))
                .order_by(ReadingMapItem.order_index)
            )
        ).scalars().all()

        threads = (
            await self._session.execute(
                select(KnowledgeThread)
                .options(
                    selectinload(KnowledgeThread.steps).selectinload(
                        KnowledgeThreadStep.concept
                    )
                )
                .order_by(KnowledgeThread.order_index)
            )
        ).scalars().all()

        recent_activities = (
            await self._session.execute(
                select(LearningActivity)
                .options(selectinload(LearningActivity.lesson))
                .order_by(desc(LearningActivity.occurred_at))
                .limit(30)
            )
        ).scalars().all()

        total_items = len(items)
        completed_items = sum(
            1 for i in items if i.is_completed or i.status == "Completed"
        )

        return {
            "statistics": {
                "totalItems": total_items,
                "completedItems": completed_items,
                "progressPercentage": (
                    0 if total_items == 0 else int(completed_items / total_items * 100)
                ),
            },
            "items": [
                {
                    "id": i.id,
                    "category": i.category,
                    "title": i.title,
                    "subText": i.sub_text,
                    "orderIndex": i.order_index,
                    "isCompleted": i.is_completed,
                    "status": i.status,
                    "scheduledFor": i.scheduled_for.isoformat()
                    if i.scheduled_for is not None
                    else None,
                    "priority": i.priority,
                    "isSeeded": i.is_seeded,
                    "lessonSlug": i.lesson.slug if i.lesson is not None else None,
                }
                for i in items
            ],
            "threads": [
                {
                    "id": t.id,
                    "domain": t.domain,
                    "rawPath": t.raw_path,
                    "steps": [
                        {
                            "orderIndex": s.order_index,
                            "label": s.label,
                            "conceptSlug": s.concept.slug if s.concept is not None else None,
                        }
                        for s in sorted(t.steps, key=lambda x: x.order_index)
                    ],
                }
                for t in threads
            ],
            "recentActivities": [
                {
                    "id": a.id,
                    "eventType": a.event_type,
                    "occurredAt": format_dotnet_datetime(a.occurred_at),
                    "lessonId": a.lesson_id,
                    "lessonTitle": a.lesson.title if a.lesson is not None else None,
                }
                for a in recent_activities
            ],
        }
