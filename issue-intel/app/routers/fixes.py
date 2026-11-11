"""Fix routers: request-fix, candidates, attempts, PR records, backports."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.agents.candidates import consider_run
from app.governance.audience import apply_profile, hide_fields_for
from app.governance.rls import service_session
from app.models.g3 import FinalCheck, FixAttempt, FixCandidate, FixPr
from app.settings import get_settings

router = APIRouter()


class BackportPayload(BaseModel):
    branches: list[str]


@router.post("/runs/{run_id}/request-fix")
async def request_fix(run_id: str) -> dict[str, Any]:
    from app.models.g2 import Job, Run

    async with service_session() as session:
        run = (
            await session.execute(select(Run).where(Run.id == run_id))
        ).scalar_one_or_none()
        if run is None:
            raise HTTPException(status_code=404, detail="unknown run")
    candidate = await consider_run(get_settings(), run_id)
    if candidate.status == "PENDING":
        async with service_session() as session:
            session.add(Job(kind="fix", payload={"candidate_id": candidate.id}))
            await session.commit()
    return {"candidate_id": candidate.id, "status": candidate.status}


@router.get("/fixes/candidates")
async def list_candidates(
    status: str | None = None, run_id: str | None = None
) -> list[dict[str, Any]]:
    async with service_session() as session:
        query = select(FixCandidate).order_by(FixCandidate.id.desc()).limit(50)
        if status:
            query = query.where(FixCandidate.status == status)
        if run_id:
            query = query.where(FixCandidate.run_id == run_id)
        rows = (await session.execute(query)).scalars().all()
        return [
            {"id": c.id, "run_id": c.run_id, "ticket": c.ticket_key,
             "module": c.module, "confidence": c.confidence, "status": c.status}
            for c in rows
        ]


@router.get("/fixes/candidates/{candidate_id}")
async def get_candidate(candidate_id: int) -> dict[str, Any]:
    async with service_session() as session:
        candidate = await session.get(FixCandidate, candidate_id)
        if candidate is None:
            raise HTTPException(status_code=404, detail="unknown candidate")
        attempts = (
            await session.execute(
                select(FixAttempt).where(FixAttempt.candidate_id == candidate_id)
                .order_by(FixAttempt.attempt_no)
            )
        ).scalars().all()
        return {
            "id": candidate.id, "run_id": candidate.run_id,
            "ticket": candidate.ticket_key, "status": candidate.status,
            "attempts": [{"id": a.id, "attempt_no": a.attempt_no,
                          "status": a.status, "branch": a.branch} for a in attempts],
        }


@router.get("/fixes/attempts/{attempt_id}")
async def get_attempt(attempt_id: int) -> dict[str, Any]:
    async with service_session() as session:
        attempt = await session.get(FixAttempt, attempt_id)
        if attempt is None:
            raise HTTPException(status_code=404, detail="unknown attempt")
        prs = (
            await session.execute(
                select(FixPr).where(FixPr.attempt_id == attempt_id)
            )
        ).scalars().all()
        checks = (
            await session.execute(
                select(FinalCheck).where(FinalCheck.attempt_id == attempt_id)
                .order_by(FinalCheck.id.desc())
            )
        ).scalars().all()
        return {
            "id": attempt.id, "candidate_id": attempt.candidate_id,
            "attempt_no": attempt.attempt_no, "status": attempt.status,
            "branch": attempt.branch, "trace": attempt.trace,
            "tokens_in": attempt.tokens_in, "tokens_out": attempt.tokens_out,
            "build_output": attempt.build_output[-4000:],
            "test_output": attempt.test_output[-4000:],
            "prs": [{"id": p.id, "kind": p.kind, "branch": p.branch,
                     "base": p.base, "status": p.status} for p in prs],
            "final_checks": [{"verdict": c.verdict, "reason": c.reason}
                             for c in checks],
        }


@router.get("/prs/{pr_id}")
async def get_pr(pr_id: int, audience: str = "SE_ENGINEER") -> dict[str, Any]:
    async with service_session() as session:
        pr = await session.get(FixPr, pr_id)
        if pr is None:
            raise HTTPException(status_code=404, detail="unknown PR")
        view = {
            "id": pr.id, "kind": pr.kind, "branch": pr.branch, "base": pr.base,
            "title": pr.title, "root_cause": pr.root_cause,
            "citations": pr.citations, "risk_note": pr.risk_note,
            "test_results": pr.test_results, "diff": pr.diff,
            "status": pr.status, "attempt_id": pr.attempt_id,
        }
    return apply_profile(view, await hide_fields_for(audience))


@router.post("/prs/{pr_id}/request-backport")
async def request_backport(pr_id: int, payload: BackportPayload) -> dict[str, Any]:
    from app.models.g2 import Job

    async with service_session() as session:
        pr = await session.get(FixPr, pr_id)
        if pr is None:
            raise HTTPException(status_code=404, detail="unknown PR")
        if pr.status != "MERGED":
            raise HTTPException(status_code=400, detail="only merged fixes backport")
        session.add(Job(kind="backport",
                        payload={"pr_id": pr_id, "branches": payload.branches}))
        await session.commit()
        return {"queued": True, "branches": payload.branches}
