"""Ported from api/Data/ReadingMapSeedData.cs."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.knowledge_thread import KnowledgeThread
from ..models.reading_activity_log import ReadingActivityLog
from ..models.reading_map_item import ReadingMapItem


async def seed(session: AsyncSession) -> None:
    # 1. Seed Reading Map Items
    exists = (await session.execute(select(ReadingMapItem.id).limit(1))).first()
    if exists is None:
        now = datetime.now(UTC)
        session.add_all(
            [
                # Read this week
                _item("ReadThisWeek", "Virtual threads", 1, True, now),
                _item("ReadThisWeek", "Structured concurrency", 2, True, now),
                _item("ReadThisWeek", "Structured concurrency (8)", 3, True, now),
                _item("ReadThisWeek", "Structured concurrency", 4, True, now),
                # Revisited
                _item("Revisited", "Spring async and resilience", 1, False, now),
                # Deferred
                _item("Deferred", "Next sometime", 1, False, now),
                _item("Deferred", "Deferred tomorrow", 2, False, now),
                # Lists
                _item("Lists", "APIs in (2)", 1, False, now),
                _item("Lists", "Deferred (1)", 2, False, now),
                # Prerequisites
                _item("Prerequisites", "Java Concurrency", 1, False, now),
            ]
        )

    # 2. Seed Reading Activity Logs (7-day timeline sparkline matching Study-tracker.png)
    exists = (await session.execute(select(ReadingActivityLog.id).limit(1))).first()
    if exists is None:
        now = datetime.now(UTC)
        session.add_all(
            [
                _log("Mon", 1, 1, now - timedelta(days=7)),
                _log("Tue", 1, 2, now - timedelta(days=6)),
                _log("Wed", 3, 3, now - timedelta(days=5)),
                _log("Thu", 6, 4, now - timedelta(days=4)),
                _log("Fri", 2, 5, now - timedelta(days=3)),
                _log("Sat", 4, 6, now - timedelta(days=2)),
                _log("Sun", 0, 7, now - timedelta(days=1)),
                _log("Sun", 5, 8, now),
            ]
        )

    # 3. Seed Knowledge Threads (Linear semantic progression pipelines)
    exists = (await session.execute(select(KnowledgeThread.id).limit(1))).first()
    if exists is None:
        session.add_all(
            [
                KnowledgeThread(
                    domain="Java",
                    raw_path="Java → concurrency → virtual threads → structured concurrency",
                    order_index=1,
                ),
                KnowledgeThread(
                    domain="Backend",
                    raw_path="Backend → APIs → async processing → resilience",
                    order_index=2,
                ),
                KnowledgeThread(
                    domain="Cloud",
                    raw_path="Cloud → containers → orchestration → networking",
                    order_index=3,
                ),
            ]
        )
    await session.flush()


def _item(
    category: str, title: str, order_index: int, is_completed: bool, now: datetime
) -> ReadingMapItem:
    return ReadingMapItem(
        category=category,
        title=title,
        order_index=order_index,
        is_completed=is_completed,
        created_at=now,
        updated_at=now,
        status="Planned",
        priority=0,
        is_seeded=False,
    )


def _log(day_label: str, count: int, order_index: int, log_date: datetime) -> ReadingActivityLog:
    return ReadingActivityLog(
        day_label=day_label,
        activity_count=count,
        order_index=order_index,
        log_date=log_date,
    )
