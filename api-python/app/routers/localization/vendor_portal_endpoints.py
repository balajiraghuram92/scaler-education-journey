"""Ported from api/Endpoints/Localization/VendorPortalEndpoints.cs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_session
from ...errors import endpoint_problem
from ...schemas.localization_dtos import UpdateTranslationRequest
from ...services.localization.localization_exceptions import (
    InvalidJobStateException,
    LocalizationStringNotFoundException,
    MarketplaceJobNotFoundException,
    VendorNotFoundException,
)
from ...services.localization.vendor_portal_service import VendorPortalService

router = APIRouter(tags=["localization-vendor"])


def _vendor_service(session: AsyncSession) -> VendorPortalService:
    return VendorPortalService(session)


@router.get("/api/localization/vendor/roster")
async def get_roster(
    request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        roster = await _vendor_service(session).get_vendor_roster_async()
        return roster
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error retrieving vendor roster.", str(exc)
        )


@router.get("/api/localization/vendor/{vendor_id:int}/jobs")
async def get_jobs(
    vendor_id: int, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        jobs = await _vendor_service(session).get_jobs_for_vendor_async(vendor_id)
        return jobs
    except VendorNotFoundException as exc:
        return endpoint_problem(request, 404, "Vendor not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(request, 500, "Error retrieving jobs.", str(exc))


@router.get("/api/localization/vendor/jobs/{job_id:int}/strings")
async def get_job_strings(
    job_id: int, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        strings = await _vendor_service(session).get_job_strings_async(job_id)
        return strings
    except MarketplaceJobNotFoundException as exc:
        return endpoint_problem(request, 404, "Job not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error retrieving job strings.", str(exc)
        )


@router.put("/api/localization/vendor/jobs/{job_id:int}/strings/{string_id:int}")
async def update_job_string(
    job_id: int,
    string_id: int,
    body: UpdateTranslationRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    # C# binds the full VendorStringRowDto here but only reads TargetText;
    # UpdateTranslationRequest carries that field and ignores the rest, so
    # well-formed bodies behave identically (Finding: an extra field with a
    # wrong JSON type 400s in C# but is ignored here).
    try:
        updated = await _vendor_service(session).update_job_string_async(
            job_id, string_id, body.target_text
        )
        await session.commit()
        return updated
    except MarketplaceJobNotFoundException as exc:
        return endpoint_problem(request, 404, "Job not found.", str(exc))
    except LocalizationStringNotFoundException as exc:
        return endpoint_problem(request, 404, "String not found.", str(exc))
    except InvalidJobStateException as exc:
        return endpoint_problem(request, 409, "Invalid job state.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error updating job string.", str(exc)
        )


@router.post("/api/localization/vendor/jobs/{job_id:int}/submit")
async def submit_job(
    job_id: int, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        job = await _vendor_service(session).submit_job_for_review_async(job_id)
        await session.commit()
        return job
    except MarketplaceJobNotFoundException as exc:
        return endpoint_problem(request, 404, "Job not found.", str(exc))
    except InvalidJobStateException as exc:
        return endpoint_problem(request, 409, "Invalid job state.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error submitting job for review.", str(exc)
        )
