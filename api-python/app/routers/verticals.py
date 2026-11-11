"""Ported from api/Program.cs inline routes for /api/verticals (lines 679-772)."""

from __future__ import annotations

import re
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import get_session
from ..models.study_task import StudyTask
from ..models.study_vertical import StudyVertical
from ..schemas.base import CamelModel, format_dotnet_datetime

router = APIRouter(tags=["verticals"])


class CreateVerticalRequest(CamelModel):
    name: str | None = None
    description: str | None = None


class IngestRequest(CamelModel):
    vertical_id: int | None = None
    name: str | None = None
    description: str | None = None
    markdown_content: str | None = None


def vertical_to_dict(vertical: StudyVertical) -> dict:
    tasks = vertical.tasks or []
    has_modules = any(t.module and t.module != "General" for t in tasks)
    return {
        "id": vertical.id,
        "name": vertical.name,
        "description": vertical.description,
        "canonicalVerticalId": vertical.canonical_vertical_id,
        "archivedAt": format_dotnet_datetime(vertical.archived_at)
        if vertical.archived_at is not None
        else None,
        "updatedAt": format_dotnet_datetime(vertical.updated_at),
        "tasks": [task_to_dict(t) for t in tasks],
        "layoutMode": "Modular" if has_modules else "Flat",
    }


def task_to_dict(task: StudyTask) -> dict:
    return {
        "id": task.id,
        "verticalId": task.vertical_id,
        "title": task.title,
        "isCompleted": task.is_completed,
        "module": task.module,
        "updatedAt": format_dotnet_datetime(task.updated_at),
    }


_HEADER_RE = re.compile(r"^##\s+(.+)$")
_TASK_RE = re.compile(r"^- \[([ xX])\]\s+(.+)$")


def parse_markdown_to_tasks(markdown: str) -> list[StudyTask]:
    """Ported from the ParseMarkdownToTasks helper at the bottom of Program.cs."""
    tasks: list[StudyTask] = []
    if not markdown or not markdown.strip():
        return tasks
    current_module = "General"
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        header_match = _HEADER_RE.match(line)
        if header_match:
            current_module = header_match.group(1).strip()
            continue
        task_match = _TASK_RE.match(line)
        if task_match:
            is_completed = task_match.group(1).lower() == "x"
            tasks.append(
                StudyTask(
                    title=task_match.group(2).strip(),
                    is_completed=is_completed,
                    module=current_module,
                )
            )
    return tasks


@router.get("/api/verticals")  # Program.cs line 679
async def get_verticals(session: AsyncSession = Depends(get_session)):
    verticals = (
        await session.execute(
            select(StudyVertical).options(selectinload(StudyVertical.tasks))
        )
    ).scalars().all()
    return [vertical_to_dict(v) for v in verticals]


@router.get("/api/verticals/{vertical_id}")  # Program.cs line 683
async def get_vertical_by_id(
    vertical_id: int, session: AsyncSession = Depends(get_session)
):
    vertical = (
        await session.execute(
            select(StudyVertical)
            .options(selectinload(StudyVertical.tasks))
            .where(StudyVertical.id == vertical_id)
        )
    ).scalar_one_or_none()
    if vertical is None:
        return Response(status_code=404)
    return vertical_to_dict(vertical)


@router.post("/api/verticals")  # Program.cs line 693
async def create_vertical(
    body: CreateVerticalRequest, session: AsyncSession = Depends(get_session)
):
    if not body.name or not body.name.strip():
        return JSONResponse(status_code=400, content={"message": "Name is required."})
    vertical = StudyVertical(
        name=body.name,
        description=body.description if body.description is not None else "",
        updated_at=datetime.now(UTC),
    )
    session.add(vertical)
    await session.commit()
    await session.refresh(vertical, ["tasks"])
    return JSONResponse(
        status_code=201,
        headers={"Location": f"/api/verticals/{vertical.id}"},
        content=vertical_to_dict(vertical),
    )


@router.post("/api/verticals/ingest")  # Program.cs line 713
async def ingest_vertical_markdown(
    body: IngestRequest, session: AsyncSession = Depends(get_session)
):
    if not body.markdown_content or not body.markdown_content.strip():
        return JSONResponse(
            status_code=400, content={"message": "Markdown content is required."}
        )
    parsed_tasks = parse_markdown_to_tasks(body.markdown_content)
    if body.vertical_id is not None and body.vertical_id > 0:
        vertical = (
            await session.execute(
                select(StudyVertical)
                .options(selectinload(StudyVertical.tasks))
                .where(StudyVertical.id == body.vertical_id)
            )
        ).scalar_one_or_none()
        if vertical is None:
            return JSONResponse(
                status_code=404,
                content={"message": f"Vertical with ID {body.vertical_id} not found."},
            )
        if body.name and body.name.strip():
            vertical.name = body.name
        if body.description is not None:
            vertical.description = body.description
        for task in list(vertical.tasks):
            await session.delete(task)
        for task in parsed_tasks:
            task.vertical_id = vertical.id
            task.updated_at = datetime.now(UTC)
            session.add(task)
        await session.commit()
        await session.refresh(vertical, ["tasks"])
        return vertical_to_dict(vertical)
    vertical = StudyVertical(
        name=body.name if body.name and body.name.strip() else "New Vertical",
        description=body.description if body.description is not None else "",
        updated_at=datetime.now(UTC),
    )
    session.add(vertical)
    await session.flush()
    for task in parsed_tasks:
        task.vertical_id = vertical.id
        task.updated_at = datetime.now(UTC)
        session.add(task)
    await session.commit()
    await session.refresh(vertical, ["tasks"])
    return JSONResponse(
        status_code=201,
        headers={"Location": f"/api/verticals/{vertical.id}"},
        content=vertical_to_dict(vertical),
    )
