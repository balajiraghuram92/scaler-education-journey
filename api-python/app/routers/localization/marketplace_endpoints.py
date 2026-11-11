"""Ported from api/Endpoints/Localization/MarketplaceEndpoints.cs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_session
from ...errors import endpoint_problem
from ...services.localization.credit_ledger_service import CreditLedgerService
from ...services.localization.localization_exceptions import (
    InvalidJobStateException,
    LocalizationLocaleNotFoundException,
    LocalizationProjectNotFoundException,
    MarketplaceBidNotFoundException,
    MarketplaceJobNotFoundException,
)
from ...services.localization.marketplace_service import MarketplaceService

router = APIRouter(tags=["localization-marketplace"])


def _marketplace_service(session: AsyncSession) -> MarketplaceService:
    return MarketplaceService(session, CreditLedgerService(session))


@router.get("/api/localization/projects/{slug}/marketplace")
async def get_overview(
    slug: str, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        overview = await _marketplace_service(session).get_locale_overview_async(slug)
        return overview
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error retrieving marketplace overview.", str(exc)
        )


@router.post("/api/localization/projects/{slug}/marketplace/{locale_code}/post")
async def post_to_marketplace(
    slug: str,
    locale_code: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        job = await _marketplace_service(session).post_to_marketplace_async(
            slug, locale_code
        )
        await session.commit()
        return job
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except LocalizationLocaleNotFoundException as exc:
        return endpoint_problem(request, 404, "Locale not found.", str(exc))
    except InvalidJobStateException as exc:
        return endpoint_problem(request, 409, "Invalid job state.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error posting to marketplace.", str(exc)
        )


@router.get("/api/localization/marketplace/jobs/{job_id}/bids")
async def get_bids(
    job_id: int, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        bids = await _marketplace_service(session).get_bids_async(job_id)
        return bids
    except MarketplaceJobNotFoundException as exc:
        return endpoint_problem(request, 404, "Job not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(request, 500, "Error retrieving bids.", str(exc))


@router.post("/api/localization/marketplace/jobs/{job_id}/bids/{bid_id}/award")
async def award_bid(
    job_id: int,
    bid_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        job = await _marketplace_service(session).award_bid_async(job_id, bid_id)
        await session.commit()
        return job
    except MarketplaceJobNotFoundException as exc:
        return endpoint_problem(request, 404, "Job not found.", str(exc))
    except MarketplaceBidNotFoundException as exc:
        return endpoint_problem(request, 404, "Bid not found.", str(exc))
    except InvalidJobStateException as exc:
        return endpoint_problem(request, 409, "Invalid job state.", str(exc))
    except Exception as exc:
        return endpoint_problem(request, 500, "Error awarding bid.", str(exc))


@router.post("/api/localization/marketplace/jobs/{job_id}/approve")
async def approve_submission(
    job_id: int, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        job = await _marketplace_service(session).approve_submission_async(job_id)
        await session.commit()
        return job
    except MarketplaceJobNotFoundException as exc:
        return endpoint_problem(request, 404, "Job not found.", str(exc))
    except InvalidJobStateException as exc:
        return endpoint_problem(request, 409, "Invalid job state.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error approving submission.", str(exc)
        )


@router.post("/api/localization/marketplace/jobs/{job_id}/send-back")
async def send_back_for_revision(
    job_id: int, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        job = await _marketplace_service(session).send_back_for_revision_async(job_id)
        await session.commit()
        return job
    except MarketplaceJobNotFoundException as exc:
        return endpoint_problem(request, 404, "Job not found.", str(exc))
    except InvalidJobStateException as exc:
        return endpoint_problem(request, 409, "Invalid job state.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error sending back for revision.", str(exc)
        )
