"""Ported from api/Endpoints/Localization/UsageEndpoints.cs."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_session
from ...errors import endpoint_problem
from ...models.app_user import AppUser
from ...models.localization.localization_project import LocalizationProject
from ...models.localization.localization_provider_rate import LocalizationProviderRate
from ...models.localization.localization_usage_cap import LocalizationUsageCap
from ...models.localization.usage_constants import (
    UsageCapKinds,
    UsageMeters,
    UsageUnitKinds,
)
from ...models.localization.vendor import Vendor
from ...schemas.localization_dtos import (
    AddProviderRateRequest,
    OpsVendorTeamDto,
    ProjectControlsDto,
    ProviderRateDto,
    SaveAgreementRequest,
    UsageCapDto,
)
from ...services.auth.current_user import CurrentUser, get_current_user_optional
from ...services.localization.localization_exceptions import (
    LocalizationProjectNotFoundException,
)
from ...services.localization.translation_job_service import TranslationJobService
from ...services.localization.usage_metering_service import UsageMeteringService

router = APIRouter(tags=["localization-ops"])

# Mirrors DateTime.TryParseExact(month, "yyyy-MM", InvariantCulture, None):
# exactly four year digits and two month digits, no whitespace tolerance.
_MONTH_RE = re.compile(r"^(\d{4})-(\d{2})$")

_MAX_INT64 = 9223372036854775807


async def _load_approved_admin(
    session: AsyncSession, current: CurrentUser
) -> AppUser | None:
    # Same check as the admin router (C# AdminAuthorization): the ops routes
    # carry no Authorize attribute, so a signed-out caller gets this 403 body
    # too — there is deliberately no require_admin dependency here.
    if current.user_id is None:
        return None
    admin = (
        await session.execute(select(AppUser).where(AppUser.id == current.user_id))
    ).scalar_one_or_none()
    if admin is None or admin.role != "Admin" or admin.status != "Approved":
        return None
    return admin


def _forbidden(request: Request) -> JSONResponse:
    return endpoint_problem(
        request, 403, "Forbidden", "Administrative privileges required."
    )


@router.get("/api/localization/ops/usage")
async def get_usage_summary(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current: CurrentUser = Depends(get_current_user_optional),
    project: str | None = None,
    month: str | None = None,
):
    if await _load_approved_admin(session, current) is None:
        return _forbidden(request)

    now = datetime.now(UTC)
    year = now.year
    month_number = now.month
    if month is not None and month.strip():
        match = _MONTH_RE.match(month)
        if match is None:
            return endpoint_problem(
                request,
                400,
                "Invalid month.",
                "Query parameter 'month' must be in yyyy-MM format.",
            )
        year, month_number = int(match.group(1)), int(match.group(2))
        if not 1 <= year <= 9999 or not 1 <= month_number <= 12:
            return endpoint_problem(
                request,
                400,
                "Invalid month.",
                "Query parameter 'month' must be in yyyy-MM format.",
            )

    try:
        summary = await UsageMeteringService(session).get_summary_async(
            project, year, month_number
        )
        return summary
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))


@router.get("/api/localization/ops/usage/events")
async def get_usage_events(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current: CurrentUser = Depends(get_current_user_optional),
    project: str | None = None,
    limit: int | None = None,
):
    if await _load_approved_admin(session, current) is None:
        return _forbidden(request)

    try:
        events = await UsageMeteringService(session).get_recent_events_async(
            project, limit if limit is not None else 100
        )
        return events
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))


@router.get("/api/localization/ops/rates")
async def get_rates(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current: CurrentUser = Depends(get_current_user_optional),
):
    if await _load_approved_admin(session, current) is None:
        return _forbidden(request)

    rows = (
        await session.execute(
            select(LocalizationProviderRate).order_by(
                LocalizationProviderRate.valid_from.desc()
            )
        )
    ).scalars().all()
    return [
        ProviderRateDto(
            id=r.id,
            meter=r.meter,
            unit_kind=r.unit_kind,
            usd_per_million=r.usd_per_million,
            valid_from=r.valid_from,
        )
        for r in rows
    ]


@router.post("/api/localization/ops/rates")
async def add_rate(
    body: AddProviderRateRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current: CurrentUser = Depends(get_current_user_optional),
):
    if await _load_approved_admin(session, current) is None:
        return _forbidden(request)

    meters = (
        UsageMeters.MACHINE_TRANSLATION,
        UsageMeters.LLM_OPTIMIZE,
        UsageMeters.LLM_SCORE,
    )
    kinds = (
        UsageUnitKinds.CHAR,
        UsageUnitKinds.INPUT_TOKEN,
        UsageUnitKinds.OUTPUT_TOKEN,
    )
    if body.meter is None or not body.meter.strip() or body.meter not in meters:
        return endpoint_problem(
            request,
            400,
            "Unknown meter.",
            f"Meter '{body.meter or ''}' is not a known usage meter.",
        )
    if (
        body.unit_kind is None
        or not body.unit_kind.strip()
        or body.unit_kind not in kinds
    ):
        return endpoint_problem(
            request,
            400,
            "Unknown unit kind.",
            f"Unit kind '{body.unit_kind or ''}' is not a known unit kind.",
        )
    if body.usd_per_million is None or body.usd_per_million < 0:
        return endpoint_problem(
            request,
            400,
            "Invalid price.",
            "UsdPerMillion is required and must not be negative.",
        )

    valid_from = body.valid_from or datetime.now(UTC)
    duplicate = (
        await session.execute(
            select(LocalizationProviderRate.id).where(
                LocalizationProviderRate.meter == body.meter,
                LocalizationProviderRate.unit_kind == body.unit_kind,
                LocalizationProviderRate.valid_from == valid_from,
            )
        )
    ).scalar_one_or_none()
    if duplicate is not None:
        return endpoint_problem(
            request,
            409,
            "Rate already exists.",
            f"A rate for meter '{body.meter}', unit kind '{body.unit_kind}' "
            "and this valid-from already exists.",
        )

    rate = LocalizationProviderRate(
        meter=body.meter,
        unit_kind=body.unit_kind,
        usd_per_million=body.usd_per_million,
        valid_from=valid_from,
    )
    session.add(rate)
    await session.commit()
    dto = ProviderRateDto(
        id=rate.id,
        meter=rate.meter,
        unit_kind=rate.unit_kind,
        usd_per_million=rate.usd_per_million,
        valid_from=rate.valid_from,
    )
    return JSONResponse(
        status_code=201, content=dto.model_dump(mode="json", by_alias=True)
    )


@router.get("/api/localization/ops/projects/{slug}/controls")
async def get_controls(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current: CurrentUser = Depends(get_current_user_optional),
):
    if await _load_approved_admin(session, current) is None:
        return _forbidden(request)

    project = (
        await session.execute(
            select(LocalizationProject).where(LocalizationProject.slug == slug)
        )
    ).scalar_one_or_none()
    if project is None:
        return endpoint_problem(
            request,
            404,
            "Project not found.",
            f"Localization project '{slug}' was not found.",
        )
    return await _controls_dto(session, project)


@router.put("/api/localization/ops/projects/{slug}/controls")
async def update_controls(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current: CurrentUser = Depends(get_current_user_optional),
):
    if await _load_approved_admin(session, current) is None:
        return _forbidden(request)

    project = (
        await session.execute(
            select(LocalizationProject).where(LocalizationProject.slug == slug)
        )
    ).scalar_one_or_none()
    if project is None:
        return endpoint_problem(
            request,
            404,
            "Project not found.",
            f"Localization project '{slug}' was not found.",
        )

    # Every field is optional: absent leaves the value unchanged, explicit
    # null on a limit removes the cap. The raw JSON body is read so absent
    # and null stay distinguishable.
    body: Any = await request.json()
    props: dict[str, Any] = body if isinstance(body, dict) else {}

    if "aiEnabled" in props and props["aiEnabled"] is not None:
        if not isinstance(props["aiEnabled"], bool):
            return endpoint_problem(
                request,
                400,
                "Invalid controls.",
                "Property 'aiEnabled' must be a boolean.",
            )
        project.ai_enabled = props["aiEnabled"]

    limits = (
        ("machineTranslationMonthlyLimit", UsageCapKinds.MACHINE_TRANSLATION),
        ("llmMonthlyLimit", UsageCapKinds.LLM),
    )
    for prop, kind in limits:
        if prop not in props:
            continue
        value = props[prop]
        if value is None:
            doomed = (
                await session.execute(
                    select(LocalizationUsageCap).where(
                        LocalizationUsageCap.project_id == project.id,
                        LocalizationUsageCap.kind == kind,
                    )
                )
            ).scalar_one_or_none()
            if doomed is not None:
                await session.delete(doomed)
            continue
        # C# JsonElement.TryGetInt64: bools, fraction strings, floats and
        # out-of-range integers all fail, as does anything negative.
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value < 0
            or value > _MAX_INT64
        ):
            return endpoint_problem(
                request,
                400,
                "Invalid controls.",
                f"Property '{prop}' must be a non-negative integer or null.",
            )
        existing = (
            await session.execute(
                select(LocalizationUsageCap).where(
                    LocalizationUsageCap.project_id == project.id,
                    LocalizationUsageCap.kind == kind,
                )
            )
        ).scalar_one_or_none()
        if existing is None:
            session.add(
                LocalizationUsageCap(
                    project_id=project.id,
                    kind=kind,
                    monthly_limit=value,
                    updated_at=datetime.now(UTC),
                )
            )
        else:
            existing.monthly_limit = value
            existing.updated_at = datetime.now(UTC)

    await session.commit()
    return await _controls_dto(session, project)


@router.get("/api/localization/ops/teams")
async def get_teams(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current: CurrentUser = Depends(get_current_user_optional),
):
    if await _load_approved_admin(session, current) is None:
        return _forbidden(request)

    vendors = (
        await session.execute(select(Vendor).order_by(Vendor.id))
    ).scalars().all()
    return [
        OpsVendorTeamDto(
            id=v.id, alias=v.alias, real_name=v.name, languages=v.languages
        )
        for v in vendors
    ]


@router.get("/api/localization/ops/projects/{slug}/agreement")
async def get_ops_agreement(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current: CurrentUser = Depends(get_current_user_optional),
):
    if await _load_approved_admin(session, current) is None:
        return _forbidden(request)

    try:
        agreement = await TranslationJobService(session).get_agreement_async(
            slug, True
        )
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


@router.put("/api/localization/ops/projects/{slug}/agreement")
async def save_ops_agreement(
    slug: str,
    body: SaveAgreementRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current: CurrentUser = Depends(get_current_user_optional),
):
    if await _load_approved_admin(session, current) is None:
        return _forbidden(request)

    try:
        agreement = await TranslationJobService(session).save_agreement_async(
            slug, body
        )
        await session.commit()
        return agreement
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except ValueError as exc:
        return endpoint_problem(request, 400, "Invalid agreement.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error saving agreement.", str(exc)
        )


async def _controls_dto(
    session: AsyncSession, project: LocalizationProject
) -> ProjectControlsDto:
    budget = await UsageMeteringService(session).begin_run_async(
        project.id, datetime.now(UTC)
    )
    return ProjectControlsDto(
        project_slug=project.slug,
        ai_enabled=project.ai_enabled,
        caps=[
            UsageCapDto(
                kind=kind, monthly_limit=budget.limit(kind), used=budget.used(kind)
            )
            for kind in (
                UsageCapKinds.MACHINE_TRANSLATION,
                UsageCapKinds.LLM,
            )
        ],
    )
