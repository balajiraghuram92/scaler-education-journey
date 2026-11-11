"""Ported from api/Endpoints/ImportEndpoints.cs."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..services.curriculum_import_service import (
    CurriculumImportRequest,
    CurriculumImportService,
)

router = APIRouter(tags=["import"])


@router.post("/api/v2/curriculum/import")
async def import_chapter(
    body: CurriculumImportRequest, session: AsyncSession = Depends(get_session)
):
    result = await CurriculumImportService(session).import_chapter(body)
    await session.commit()
    if result.success:
        return result
    return JSONResponse(status_code=400, content=result.model_dump(by_alias=True, mode="json"))
