"""Ported from api/Program.cs inline routes for /api/reading-map (lines 1237-1319)."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models.knowledge_thread import KnowledgeThread
from ..models.reading_activity_log import ReadingActivityLog
from ..models.reading_map_item import ReadingMapItem
from ..schemas.dtos import (
    CreateReadingItemRequest,
    DailyActivityDto,
    KnowledgeThreadDto,
    ReadingMapDto,
    ReadingMapItemDto,
)

router = APIRouter(tags=["reading-map"])


def _item_to_dto(item: ReadingMapItem) -> ReadingMapItemDto:
    return ReadingMapItemDto(
        id=item.id,
        category=item.category,
        title=item.title,
        sub_text=item.sub_text,
        is_completed=item.is_completed,
        order_index=item.order_index,
    )


@router.get("/api/reading-map")  # Program.cs line 1237
async def get_reading_map(session: AsyncSession = Depends(get_session)):
    items = (
        await session.execute(
            select(ReadingMapItem).order_by(ReadingMapItem.order_index)
        )
    ).scalars().all()
    activities = (
        await session.execute(
            select(ReadingActivityLog).order_by(ReadingActivityLog.order_index)
        )
    ).scalars().all()
    threads = (
        await session.execute(
            select(KnowledgeThread).order_by(KnowledgeThread.order_index)
        )
    ).scalars().all()

    def map_dto(category: str) -> list[ReadingMapItemDto]:
        return [
            _item_to_dto(i) for i in items if i.category.lower() == category.lower()
        ]

    return ReadingMapDto(
        read_this_week=map_dto("ReadThisWeek"),
        revisited=map_dto("Revisited"),
        deferred=map_dto("Deferred"),
        lists=map_dto("Lists"),
        prerequisites=map_dto("Prerequisites"),
        activity_timeline=[
            DailyActivityDto(
                id=a.id,
                day_label=a.day_label,
                activity_count=a.activity_count,
                order_index=a.order_index,
            )
            for a in activities
        ],
        knowledge_threads=[
            KnowledgeThreadDto(
                id=t.id,
                domain=t.domain,
                raw_path=t.raw_path,
                nodes=[s.strip() for s in t.raw_path.split("→") if s.strip()],
                order_index=t.order_index,
            )
            for t in threads
        ],
    )


@router.patch("/api/reading-map/items/{item_id:int}/toggle")  # Program.cs line 1280
async def toggle_reading_map_item(
    item_id: int, session: AsyncSession = Depends(get_session)
):
    item = await session.get(ReadingMapItem, item_id)
    if item is None:
        return Response(status_code=404)
    item.is_completed = not item.is_completed
    item.updated_at = datetime.now(UTC)
    await session.commit()
    await session.refresh(item)
    return _item_to_dto(item)


@router.post("/api/reading-map/items")  # Program.cs line 1293
async def create_reading_map_item(
    body: CreateReadingItemRequest, session: AsyncSession = Depends(get_session)
):
    if not body.title or not body.title.strip() or not body.category or not body.category.strip():
        return JSONResponse(
            status_code=400, content={"message": "Category and Title are required."}
        )
    max_order = (
        await session.execute(
            select(func.max(ReadingMapItem.order_index)).where(
                func.lower(ReadingMapItem.category) == body.category.lower()
            )
        )
    ).scalar_one()
    now = datetime.now(UTC)
    item = ReadingMapItem(
        category=body.category.strip(),
        title=body.title.strip(),
        sub_text=body.sub_text.strip() if body.sub_text is not None else None,
        order_index=body.order_index
        if body.order_index is not None
        else (max_order or 0) + 1,
        is_completed=False,
        created_at=now,
        updated_at=now,
        status="Planned",
        priority=0,
        is_seeded=False,
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return JSONResponse(
        status_code=201,
        headers={"Location": f"/api/reading-map/items/{item.id}"},
        content=_item_to_dto(item).model_dump(by_alias=True, mode="json"),
    )
