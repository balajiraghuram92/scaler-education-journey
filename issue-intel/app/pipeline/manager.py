"""Run manager: dedupe events, classify triggers, cache runs, execute stages."""
from __future__ import annotations

import datetime
import hashlib
import uuid
from typing import Any

from sqlalchemy import func, select

from app.adapters.fake_tracker import WebhookEvent
from app.gateway.gateway import ModelGateway
from app.governance.rls import service_session
from app.models.g1 import Case
from app.models.g2 import Evidence, Job, Review, Run, RunStage, Writeback
from app.pipeline import stage_fns
from app.pipeline.stages import RunContext, StageError

PIPELINE_VERSION = "g2.1"


def content_hash(title: str, body: str, version: str) -> str:
    return hashlib.sha256(f"{title}\n{body}\n{version}".encode()).hexdigest()


async def _delete_run(session: Any, run_id: str) -> None:
    for model in (Evidence, RunStage, Writeback, Review):
        rows = (
            await session.execute(select(model).where(model.run_id == run_id))
        ).scalars().all()
        for row in rows:
            await session.delete(row)
    run = (
        await session.execute(select(Run).where(Run.id == run_id))
    ).scalar_one_or_none()
    if run is not None:
        await session.delete(run)


async def handle_event(event: WebhookEvent) -> tuple[str, bool]:
    """Handle a tracker webhook. Returns (run_id, cached)."""
    async with service_session() as session:
        ticket = (
            await session.execute(select(Case).where(Case.source_key == event.key))
        ).scalar_one_or_none()
        if ticket is None:
            raise ValueError(f"unknown ticket {event.key}")
        digest = content_hash(ticket.title, ticket.body, ticket.version)
        existing = (
            await session.execute(
                select(Run).where(
                    Run.ticket_key == event.key,
                    Run.content_hash == digest,
                    Run.pipeline_version == PIPELINE_VERSION,
                )
            )
        ).scalar_one_or_none()
        if existing is not None and not event.rerun:
            return existing.id, True
        if existing is not None and event.rerun:
            await _delete_run(session, existing.id)
        prior = (
            await session.execute(
                select(func.count(Run.id)).where(Run.ticket_key == event.key)
            )
        ).scalar() or 0
        trigger = "RERUN" if event.rerun else ("NEW" if prior == 0 else "UPDATE")
        run = Run(
            id=uuid.uuid4().hex, ticket_source=ticket.source, ticket_key=ticket.source_key,
            trigger=trigger, pipeline_version=PIPELINE_VERSION,
            content_hash=digest, status="QUEUED",
        )
        session.add(run)
        session.add(Job(kind="run", payload={"run_id": run.id}))
        await session.commit()
        return run.id, False


async def execute_run(gateway: ModelGateway, run_id: str) -> None:
    """Execute stages S1..S8 for a run. Raises StageError on stage failure."""
    async with service_session() as session:
        run = (
            await session.execute(select(Run).where(Run.id == run_id))
        ).scalar_one()
        ticket = (
            await session.execute(select(Case).where(Case.source_key == run.ticket_key))
        ).scalar_one()
        run.status = "RUNNING"
        await session.commit()
        ctx = RunContext(session=session, gateway=gateway, run=run, ticket=ticket)
        try:
            for name, fn in stage_fns.STAGES:
                payload = {"ticket_key": ticket.source_key, "prior": sorted(ctx.outputs)}
                ctx.outputs[name] = await run_stage(ctx, name, payload, lambda f=fn: f(ctx))
        except StageError:
            run.status = "FAILED_AWAITING_HUMAN"
            run.finished_at = datetime.datetime.now(datetime.UTC)
            run.cost_usd = sum(
                c.cost_usd for c in gateway.logged_calls if c.run_id == run_id
            )
            await session.commit()
            raise
        run.status = "DONE"
        run.finished_at = datetime.datetime.now(datetime.UTC)
        run.cost_usd = sum(c.cost_usd for c in gateway.logged_calls if c.run_id == run_id)
        await session.commit()
