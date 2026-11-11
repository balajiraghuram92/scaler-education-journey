"""Approval routers: approve (mints token), merge, tokens, final check."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from app.adapters.fake_codehost import CODEHOST
from app.agents.sandbox import run_cmd
from app.governance.rls import service_session
from app.governance.tokens import mint_token, validate_token
from app.models.g2 import Run
from app.models.g3 import FinalCheck, FixAttempt, FixCandidate, FixPr
from app.settings import get_settings

router = APIRouter()


class ApprovePayload(BaseModel):
    approver: str


class MergePayload(BaseModel):
    token: str
    approver: str


class TokenPayload(BaseModel):
    action: str
    payload: dict[str, Any] = {}


def _repo() -> Path:
    repo = Path(get_settings().sample_repo_path)
    if not repo.is_absolute():
        here = Path("issue-intel") / repo if Path("issue-intel").exists() else repo
        return here
    return repo


@router.post("/prs/{pr_id}/approve")
async def approve_pr(pr_id: int, payload: ApprovePayload) -> dict[str, Any]:
    _ = payload
    async with service_session() as session:
        pr = await session.get(FixPr, pr_id)
        if pr is None:
            raise HTTPException(status_code=404, detail="unknown PR")
        if pr.status != "OPEN":
            raise HTTPException(status_code=400, detail="only OPEN PRs approve")
        check = (
            await session.execute(
                select(FinalCheck).where(FinalCheck.attempt_id == pr.attempt_id)
                .order_by(FinalCheck.id.desc()).limit(1)
            )
        ).scalar_one_or_none()
        if check is None or check.verdict != "OK":
            raise HTTPException(
                status_code=400, detail="final check verdict must be OK first"
            )
        attempt = await session.get(FixAttempt, pr.attempt_id)
        assert attempt is not None
        candidate = await session.get(FixCandidate, attempt.candidate_id)
        assert candidate is not None
        diff_sha = hashlib.sha256(pr.diff.encode()).hexdigest()
        token_payload = {"pr_id": pr_id, "diff_sha": diff_sha}
        token = await mint_token(
            candidate.run_id, candidate.ticket_key, "merge_pr", token_payload
        )
        return {"token": token,
                "expires_in": get_settings().approval_token_ttl_seconds}


@router.post("/prs/{pr_id}/merge")
async def merge_pr(pr_id: int, payload: MergePayload) -> dict[str, Any]:
    async with service_session() as session:
        pr = await session.get(FixPr, pr_id)
        if pr is None:
            raise HTTPException(status_code=404, detail="unknown PR")
        attempt = await session.get(FixAttempt, pr.attempt_id)
        assert attempt is not None
        candidate = await session.get(FixCandidate, attempt.candidate_id)
        assert candidate is not None
        diff_sha = hashlib.sha256(pr.diff.encode()).hexdigest()
        ok = await validate_token(
            payload.token, "merge_pr", candidate.run_id, candidate.ticket_key,
            {"pr_id": pr_id, "diff_sha": diff_sha},
        )
        if not ok:
            raise HTTPException(status_code=403, detail="invalid approval token")
        if pr.status != "OPEN":
            raise HTTPException(status_code=400, detail="only OPEN PRs merge")
        repo = _repo()
        checkout = await run_cmd(["git", "checkout", pr.base], cwd=repo, timeout_s=120)
        if checkout.returncode != 0:
            raise HTTPException(status_code=500, detail="checkout failed")
        merged = await run_cmd(["git", "merge", "--no-ff", pr.branch],
                               cwd=repo, timeout_s=180)
        if merged.returncode != 0:
            await run_cmd(["git", "merge", "--abort"], cwd=repo, timeout_s=60)
            raise HTTPException(status_code=409, detail="merge conflict in git")
        sha = await run_cmd(["git", "rev-parse", "HEAD"], cwd=repo, timeout_s=60)
        pr.status = "MERGED"
        candidate.status = "MERGED"
        await session.commit()
        CODEHOST.record_merge(pr_id, pr.branch, pr.base, payload.approver,
                              sha.stdout.strip())
        return {"merged": True, "commit": sha.stdout.strip()}


@router.post("/runs/{run_id}/tokens")
async def mint_action_token(run_id: str, payload: TokenPayload) -> dict[str, Any]:
    if payload.action not in ("publish_status", "request_fix"):
        raise HTTPException(status_code=400, detail="unknown action")
    async with service_session() as session:
        run = (
            await session.execute(select(Run).where(Run.id == run_id))
        ).scalar_one_or_none()
        if run is None:
            raise HTTPException(status_code=404, detail="unknown run")
        token = await mint_token(run_id, run.ticket_key, payload.action,
                                 payload.payload)
        return {"token": token,
                "expires_in": get_settings().approval_token_ttl_seconds}


@router.get("/runs/{run_id}/final-check")
async def get_final_check(run_id: str) -> dict[str, Any]:
    async with service_session() as session:
        check = (
            await session.execute(
                select(FinalCheck).where(FinalCheck.run_id == run_id)
                .order_by(FinalCheck.id.desc()).limit(1)
            )
        ).scalar_one_or_none()
        if check is None:
            raise HTTPException(status_code=404, detail="no final check yet")
        return {"verdict": check.verdict, "reason": check.reason,
                "attempt_id": check.attempt_id}
