"""Ported from api/Program.cs inline routes for /api/tasks (line 774)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models.study_task import StudyTask
from ..services.progress_service import ProgressService
from .verticals import task_to_dict

router = APIRouter(tags=["tasks"])


@router.put("/api/tasks/{task_id:int}/toggle")  # Program.cs line 774
async def toggle_task(task_id: int, session: AsyncSession = Depends(get_session)):
    task = await session.get(StudyTask, task_id)
    if task is None:
        return Response(status_code=404)
    result = await ProgressService(session).set_task_completion(task_id, not task.is_completed)
    if not result.success:
        return JSONResponse(status_code=400, content={"error": result.error})
    await session.commit()
    updated = await session.get(StudyTask, task_id)
    assert updated is not None
    return task_to_dict(updated)
