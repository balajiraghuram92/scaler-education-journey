"""Run routers: tracker webhook, run list, rendered view, stage trace."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.fake_tracker import TRACKER, WebhookEvent
from app.governance.entitlements import resolve_entitlements
from app.governance.rls import rls_session_dep, service_session
from app.models.g2 import Run, RunStage
from app.pipeline.manager import handle_event
from app.pipeline.render import render_for_viewer

router = APIRouter()


class WebhookPayload(BaseModel):
    event: str
    key: str
    rerun: bool = False


async def _viewer_entitlements(request: Request):  # type: ignore[no-untyped-def]
    try:
        user_id = int(request.headers.get("x-user-id", "0"))
    except ValueError:
        user_id = 0
    async with service_session() as session:
        return await resolve_entitlements(session, user_id)


@router.post("/webhooks/tracker")
async def tracker_webhook(payload: WebhookPayload) -> dict[str, Any]:
    TRACKER.receive_webhook(
        WebhookEvent(event=payload.event, key=payload.key, rerun=payload.rerun)
    )
    try:
        run_id, cached = await handle_event(
            WebhookEvent(event=payload.event, key=payload.key, rerun=payload.rerun)
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"run_id": run_id, "cached": cached}


@router.get("/runs")
async def list_runs() -> list[dict[str, Any]]:
    async with service_session() as session:
        runs = (
            await session.execute(select(Run).order_by(Run.created_at.desc()).limit(50))
        ).scalars().all()
        return [
            {"id": r.id, "ticket": r.ticket_key, "trigger": r.trigger,
             "status": r.status, "cost_usd": r.cost_usd,
             "created_at": r.created_at.isoformat()}
            for r in runs
        ]


@router.get("/runs/{run_id}")
async def get_run(run_id: str, request: Request) -> dict[str, Any]:
    ent = await _viewer_entitlements(request)
    try:
        return await render_for_viewer(run_id, ent)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/runs/{run_id}/trace")
async def get_trace(
    run_id: str, request: Request,
    session: AsyncSession = Depends(rls_session_dep),  # noqa: B008
) -> list[dict[str, Any]]:
    _ = session
    ent = await _viewer_entitlements(request)
    if "SE" not in ent.departments:
        raise HTTPException(status_code=403, detail="trace requires SE department")
    async with service_session() as service:
        stages = (
            await service.execute(
                select(RunStage).where(RunStage.run_id == run_id).order_by(RunStage.id)
            )
        ).scalars().all()
        return [
            {"stage": s.stage, "model": s.model, "input": s.input_json,
             "output": s.output_json, "tokens_in": s.tokens_in,
             "tokens_out": s.tokens_out, "latency_ms": s.latency_ms,
             "attempt": s.attempt, "status": s.status, "error": s.error}
            for s in stages
        ]
