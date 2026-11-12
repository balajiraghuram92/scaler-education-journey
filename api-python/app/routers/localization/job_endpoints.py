"""Ported from api/Endpoints/Localization/JobEndpoints.cs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_session
from ...errors import endpoint_problem
from ...services.localization.localization_exceptions import (
    InvalidJobStateException,
    LocalizationLocaleNotFoundException,
    LocalizationProjectNotFoundException,
    MarketplaceJobNotFoundException,
)
from ...services.localization.translation_job_service import TranslationJobService

router = APIRouter(tags=["localization-jobs"])


def _job_service(session: AsyncSession) -> TranslationJobService:
    return TranslationJobService(session)


@router.get("/api/localization/projects/{slug}/jobs")
async def get_jobs(
    slug: str, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        jobs = await _job_service(session).get_jobs_for_project_async(slug)
        return jobs
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error retrieving jobs.", str(exc)
        )


@router.post("/api/localization/projects/{slug}/jobs/{locale_code}")
async def create_job(
    slug: str,
    locale_code: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        job = await _job_service(session).create_job_async(slug, locale_code)
        await session.commit()
        return job
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except LocalizationLocaleNotFoundException as exc:
        return endpoint_problem(request, 404, "Locale not found.", str(exc))
    except InvalidJobStateException as exc:
        return endpoint_problem(request, 409, "Invalid job state.", str(exc))
    except Exception as exc:
        return endpoint_problem(request, 500, "Error creating job.", str(exc))


@router.post("/api/localization/jobs/{job_id:int}/approve")
async def approve_job(
    job_id: int, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        job = await _job_service(session).approve_async(job_id)
        await session.commit()
        return job
    except MarketplaceJobNotFoundException as exc:
        return endpoint_problem(request, 404, "Job not found.", str(exc))
    except InvalidJobStateException as exc:
        return endpoint_problem(request, 409, "Invalid job state.", str(exc))
    except Exception as exc:
        return endpoint_problem(request, 500, "Error approving job.", str(exc))


@router.post("/api/localization/jobs/{job_id:int}/send-back")
async def send_back_job(
    job_id: int, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        job = await _job_service(session).send_back_async(job_id)
        await session.commit()
        return job
    except MarketplaceJobNotFoundException as exc:
        return endpoint_problem(request, 404, "Job not found.", str(exc))
    except InvalidJobStateException as exc:
        return endpoint_problem(request, 409, "Invalid job state.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error sending job back for revision.", str(exc)
        )


@router.get("/api/localization/projects/{slug}/agreement")
async def get_agreement(
    slug: str, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        agreement = await _job_service(session).get_agreement_async(slug, False)
        if agreement is None:
            return endpoint_problem(
                request,
                404,
                "Agreement not found.",
                f"Localization project '{slug}' has no service agreement.",
            )
        return agreement
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error retrieving agreement.", str(exc)
        )
