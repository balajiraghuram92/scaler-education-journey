"""Background worker: polls the jobs table and executes runs, fixes, backports."""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from sqlalchemy import select

from app.gateway.gateway import ModelGateway
from app.governance.rls import service_session
from app.models.g2 import Job
from app.pipeline.manager import execute_run
from app.pipeline.stages import StageError
from app.settings import get_settings

logger = logging.getLogger("issueintel.worker")


def _repo() -> Path:
    repo = Path(get_settings().sample_repo_path)
    if not repo.is_absolute():
        return Path("issue-intel") / repo if Path("issue-intel").exists() else repo
    return repo


async def _execute_fix(candidate_id: int) -> None:
    from app.agents.final_check import run_final_check
    from app.agents.fix_loop import run_fix

    settings = get_settings()
    gateway = ModelGateway(settings=settings)
    async with service_session() as session:
        attempt = await run_fix(session, gateway, settings, candidate_id, _repo())
    if attempt.status == "OFFERED":
        from app.models.g3 import FixPr

        async with service_session() as session:
            pr = (
                await session.execute(
                    select(FixPr).where(FixPr.attempt_id == attempt.id,
                                        FixPr.kind == "FIX")
                )
            ).scalar_one_or_none()
            from app.models.g3 import FixCandidate

            candidate = await session.get(FixCandidate, attempt.candidate_id)
            assert candidate is not None
            await run_final_check(
                session, gateway, candidate.run_id, attempt.id,
                diff=pr.diff if pr else "",
                test_output=attempt.test_output,
            )


async def _execute_backport(pr_id: int, branches: list[str]) -> None:
    from app.agents.backport import backport_pr

    settings = get_settings()
    gateway = ModelGateway(settings=settings)
    async with service_session() as session:
        await backport_pr(session, gateway, settings, pr_id, branches, _repo())


async def poll_once() -> bool:
    async with service_session() as session:
        job = (
            await session.execute(
                select(Job).where(Job.status == "QUEUED")
                .order_by(Job.id).limit(1).with_for_update(skip_locked=True)
            )
        ).scalar_one_or_none()
        if job is None:
            return False
        job.status = "RUNNING"
        job.attempts += 1
        await session.commit()
        kind = job.kind
        payload = dict(job.payload)
        job_id = job.id
    gateway = ModelGateway()
    try:
        if kind == "run":
            await execute_run(gateway, str(payload.get("run_id", "")))
        elif kind == "fix":
            await _execute_fix(int(payload.get("candidate_id", 0)))
        elif kind == "backport":
            await _execute_backport(int(payload.get("pr_id", 0)),
                                    list(payload.get("branches", [])))
        else:
            raise ValueError(f"unknown job kind {kind}")
    except (StageError, Exception) as exc:
        async with service_session() as session:
            row = await session.get(Job, job_id)
            if row is not None:
                row.status = "FAILED"
                row.error = f"{type(exc).__name__}: {exc}"
                await session.commit()
        return True
    async with service_session() as session:
        row = await session.get(Job, job_id)
        if row is not None:
            row.status = "DONE"
            await session.commit()
    return True


async def main() -> None:
    while True:
        try:
            worked = await poll_once()
        except Exception:
            logger.exception("worker poll failed")
            worked = False
        await asyncio.sleep(0 if worked else 2)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
