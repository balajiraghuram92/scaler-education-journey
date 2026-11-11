"""Metrics endpoint: gateway and pipeline health in one JSON document."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.final_check import FILTERED_PREFIX
from app.gateway.routing import get_active
from app.governance.rls import service_session
from app.models.g2 import Run, RunStage
from app.models.g3 import FinalCheck, FixPr
from app.models.gateway import ModelCall

router = APIRouter()

EXPENSIVE_MODEL = "tessera-large"


async def _count(session: AsyncSession, statement: Any) -> int:
    value = (await session.execute(statement)).scalar()
    return int(value or 0)


@router.get("/metrics")
async def get_metrics() -> dict[str, Any]:
    async with service_session() as session:
        active = await get_active(session)
        n_calls = await _count(
            session,
            select(func.count(ModelCall.id)).where(ModelCall.is_shadow.is_(False)),
        )
        total_cost = (
            await session.execute(
                select(func.sum(ModelCall.cost_usd)).where(
                    ModelCall.is_shadow.is_(False)
                )
            )
        ).scalar() or 0.0
        n_billable = await _count(
            session,
            select(func.count(ModelCall.id)).where(
                ModelCall.is_shadow.is_(False), ModelCall.cached.is_(False)
            ),
        )
        n_expensive = await _count(
            session,
            select(func.count(ModelCall.id)).where(
                ModelCall.is_shadow.is_(False),
                ModelCall.cached.is_(False),
                ModelCall.model == EXPENSIVE_MODEL,
            ),
        )
        runs_done = await _count(
            session, select(func.count(Run.id)).where(Run.status == "DONE")
        )
        n_checks = await _count(session, select(func.count(FinalCheck.id)))
        n_ok = await _count(
            session,
            select(func.count(FinalCheck.id)).where(FinalCheck.verdict == "OK"),
        )
        n_filtered = await _count(
            session,
            select(func.count(FinalCheck.id)).where(
                FinalCheck.reason.startswith(FILTERED_PREFIX)
            ),
        )
        n_fix_prs = await _count(
            session, select(func.count(FixPr.id)).where(FixPr.kind == "FIX")
        )
        n_merged = await _count(
            session,
            select(func.count(FixPr.id)).where(
                FixPr.kind == "FIX", FixPr.status == "MERGED"
            ),
        )
        n_leakage = await _count(
            session,
            select(func.count(RunStage.id)).where(
                RunStage.error.like("%LeakageError%")
            ),
        )
        return {
            "cost_per_resolved_case": float(total_cost) / max(1, runs_done),
            "expensive_tier_share": n_expensive / max(1, n_billable),
            "final_check_sendback_rate": (n_checks - n_ok) / max(1, n_checks),
            "quality_verify_filtered": n_filtered,
            "fix_acceptance_rate": n_merged / max(1, n_fix_prs),
            "leakage_errors": n_leakage,
            "n_calls": n_calls,
            "total_cost_usd": float(total_cost),
            "runs_done": runs_done,
            "n_fix_prs": n_fix_prs,
            "active_routing_version": active.version if active else None,
        }
