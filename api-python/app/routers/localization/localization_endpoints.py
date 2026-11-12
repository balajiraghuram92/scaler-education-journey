"""Ported from api/Endpoints/Localization/LocalizationEndpoints.cs."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_session
from ...errors import endpoint_problem
from ...schemas.localization_dtos import (
    AddWorkflowStepRequest,
    ReorderWorkflowStepRequest,
    UpdateTranslationRequest,
    UpdateWorkflowStepRequest,
)
from ...services.localization.auto_routing_service import AutoRoutingService
from ...services.localization.credit_ledger_service import CreditLedgerService
from ...services.localization.google_translate_provider_service import (
    GoogleTranslateProviderService,
)
from ...services.localization.localization_ai_client import LocalizationAiClient
from ...services.localization.localization_exceptions import (
    LocalizationProjectNotFoundException,
    LocalizationStringNotFoundException,
    WorkflowStepBoundaryException,
    WorkflowStepNotFoundException,
)
from ...services.localization.localization_project_service import (
    LocalizationProjectService,
)
from ...services.localization.localization_string_service import (
    LocalizationStringService,
)
from ...services.localization.marketplace_service import MarketplaceService
from ...services.localization.mt_optimize_service import MtOptimizeService
from ...services.localization.qps_scoring_service import QpsScoringService
from ...services.localization.snapshot_service import SnapshotService
from ...services.localization.workflow_service import WorkflowService
from ...settings import get_settings

router = APIRouter(tags=["localization"])


def _workflow_service(session: AsyncSession) -> WorkflowService:
    settings = get_settings()
    ai_client = LocalizationAiClient(options=settings.localization_ai)
    return WorkflowService(
        session,
        GoogleTranslateProviderService(options=settings.google_translate),
        MtOptimizeService(ai_client),
        QpsScoringService(ai_client),
        AutoRoutingService(ai_client),
        MarketplaceService(session, CreditLedgerService(session)),
        settings.localization_ai,
    )


@router.get("/api/localization/projects")
async def get_projects(request: Request, session: AsyncSession = Depends(get_session)):
    try:
        projects = await LocalizationProjectService(session).get_projects_async()
        return projects
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error retrieving projects.", str(exc)
        )


@router.get("/api/localization/projects/{slug}")
async def get_project(
    slug: str, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        project = await LocalizationProjectService(session).get_project_async(slug)
        return project
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(request, 500, "Error retrieving project.", str(exc))


@router.get("/api/localization/projects/{slug}/strings")
async def get_strings(
    slug: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
    locale: str | None = None,
):
    try:
        locale_code = locale if locale and locale.strip() else "de-DE"
        strings = await LocalizationStringService(session).get_strings_async(
            slug, locale_code
        )
        return strings
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(request, 500, "Error retrieving strings.", str(exc))


@router.put("/api/localization/projects/{slug}/strings/{string_id:int}/translations/{locale_code}")
async def update_translation(
    slug: str,
    string_id: int,
    locale_code: str,
    body: UpdateTranslationRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        updated = await LocalizationStringService(session).update_translation_async(
            slug, string_id, locale_code, body
        )
        await session.commit()
        return updated
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except LocalizationStringNotFoundException as exc:
        return endpoint_problem(request, 404, "String not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(request, 500, "Error updating translation.", str(exc))


@router.get("/api/localization/projects/{slug}/workflow")
async def get_workflow(
    slug: str, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        steps = await _workflow_service(session).get_steps_async(slug)
        return steps
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error retrieving workflow steps.", str(exc)
        )


@router.post("/api/localization/projects/{slug}/workflow/steps")
async def add_workflow_step(
    slug: str,
    body: AddWorkflowStepRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        step = await _workflow_service(session).add_step_async(slug, body)
        await session.commit()
        return step
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except ValueError as exc:
        return endpoint_problem(request, 400, "Invalid workflow step.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error adding workflow step.", str(exc)
        )


@router.put("/api/localization/projects/{slug}/workflow/steps/{step_id:int}")
async def update_workflow_step(
    slug: str,
    step_id: int,
    body: UpdateWorkflowStepRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        updated = await _workflow_service(session).update_step_async(
            slug, step_id, body
        )
        await session.commit()
        return updated
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except WorkflowStepNotFoundException as exc:
        return endpoint_problem(request, 404, "Workflow step not found.", str(exc))
    except ValueError as exc:
        return endpoint_problem(request, 400, "Invalid workflow step.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error updating workflow step.", str(exc)
        )


@router.post("/api/localization/projects/{slug}/workflow/steps/{step_id:int}/reorder")
async def reorder_workflow_step(
    slug: str,
    step_id: int,
    body: ReorderWorkflowStepRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        await _workflow_service(session).reorder_step_async(
            slug, step_id, body.direction
        )
        await session.commit()
        return {"success": True}
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except WorkflowStepNotFoundException as exc:
        return endpoint_problem(request, 404, "Workflow step not found.", str(exc))
    except WorkflowStepBoundaryException as exc:
        return endpoint_problem(request, 400, "Boundary error.", str(exc))
    except ValueError as exc:
        return endpoint_problem(request, 400, "Invalid direction.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error reordering workflow step.", str(exc)
        )


@router.post("/api/localization/projects/{slug}/workflow/steps/{step_id:int}/run")
async def run_workflow_step(
    slug: str,
    step_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        updated_step = await _workflow_service(session).run_step_async(slug, step_id)
        await session.commit()
        return updated_step
    except NotImplementedError as exc:
        return endpoint_problem(request, 501, "Not yet implemented.", str(exc))
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except WorkflowStepNotFoundException as exc:
        return endpoint_problem(request, 404, "Workflow step not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error running workflow step.", str(exc)
        )


@router.delete("/api/localization/projects/{slug}/workflow/steps/{step_id:int}")
async def delete_workflow_step(
    slug: str,
    step_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    try:
        await _workflow_service(session).delete_step_async(slug, step_id)
        await session.commit()
        return Response(status_code=204)
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except WorkflowStepNotFoundException as exc:
        return endpoint_problem(request, 404, "Workflow step not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error deleting workflow step.", str(exc)
        )


@router.get("/api/localization/projects/{slug}/snapshots")
async def get_snapshots(
    slug: str, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        snapshots = await SnapshotService(session).get_snapshots_async(slug)
        return snapshots
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error retrieving snapshots.", str(exc)
        )


@router.post("/api/localization/projects/{slug}/snapshots")
async def cut_snapshot(
    slug: str, request: Request, session: AsyncSession = Depends(get_session)
):
    try:
        snapshot = await SnapshotService(session).cut_snapshot_async(slug)
        await session.commit()
        return snapshot
    except LocalizationProjectNotFoundException as exc:
        return endpoint_problem(request, 404, "Project not found.", str(exc))
    except Exception as exc:
        return endpoint_problem(
            request, 500, "Error cutting build snapshot.", str(exc)
        )
