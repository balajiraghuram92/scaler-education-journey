"""Ported from api/Endpoints/Localization/ProviderHealthEndpoints.cs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_session
from ...errors import endpoint_problem
from ...services.localization.localization_exceptions import (
    ProviderNotFoundException,
)
from ...services.localization.provider_health_service import ProviderHealthService

router = APIRouter(tags=["localization-provider-health"])


@router.get("/api/localization/provider-health")
async def get_health(
    request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        health = await ProviderHealthService(session).get_health_async()
        return health
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error retrieving provider health.", str(exc)
        )


@router.post("/api/localization/provider-health/{provider}/simulate-outage")
async def simulate_outage(
    provider: str, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        updated = await ProviderHealthService(session).simulate_outage_async(provider)
        await session.commit()
        return updated
    except ProviderNotFoundException as exc:
        return endpoint_problem(request, 404, "Provider not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(request, 500, "Error simulating outage.", str(exc))


@router.post("/api/localization/provider-health/{provider}/resolve")
async def resolve_outage(
    provider: str, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        updated = await ProviderHealthService(session).resolve_outage_async(provider)
        await session.commit()
        return updated
    except ProviderNotFoundException as exc:
        return endpoint_problem(request, 404, "Provider not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(request, 500, "Error resolving outage.", str(exc))
