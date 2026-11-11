"""Fix agent loop: plan -> patch -> build -> test -> revise. Bounded, traced.

Read top to bottom: one attempt = baseline, then at most fix_max_cycles of
(plan, read, patch, build, test). Two bounds: cycle count and token budget.
When a bound is hit the attempt ends as GAVE_UP with its trace kept.

The gate: ship tests must be green after the patch, and the patch must fix a
previously failing test (baseline failures, or the caller's hidden check when
provided). Integration into main happens only through the API.
"""
from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from sqlalchemy import func, select

from app.agents.gate import GateResult
from app.agents.sandbox import create_sandbox, remove_sandbox, run_cmd
from app.agents.tools import ToolError, Tools
from app.gateway.gateway import ModelGateway
from app.gateway.tasks import TaskType
from app.models.g1 import Case
from app.models.g2 import Evidence, Run, RunStage
from app.models.g3 import FixAttempt, FixCandidate, FixPr
from app.settings import Settings

PLAN_SYSTEM = (
    "You are fixing a bug in the Tessera Editor Tools C# solution. Reply with "
    'JSON only: {"reads": ["src/Module/File.cs", ...], "approach": "..."}.'
)
PATCH_SYSTEM = (
    "Write the fix as a unified diff from the repository root. Reply with "
    'JSON only: {"patch": "diff --git ...", "files": [...], '
    '"explanation": "..."}. Only touch allow-listed modules."'
)

HiddenCheck = Callable[[Path], Awaitable[bool]]


async def _evidence_pack(session: Any, run_id: str) -> tuple[str, list[str]]:
    rows = (
        await session.execute(select(Evidence).where(Evidence.run_id == run_id))
    ).scalars().all()
    s7 = (
        await session.execute(
            select(RunStage).where(RunStage.run_id == run_id, RunStage.stage == "S7")
        )
    ).scalar_one_or_none()
    parts = [f"[{r.evid} {r.kind}:{r.key}] {r.title}\n{r.snippet}" for r in rows]
    if s7 is not None:
        parts.append(f"Synthesis: {s7.output_json.get('answer_text', '')}")
    return "\n\n".join(parts), [r.evid for r in rows]


def _spent(gateway: ModelGateway, tag: str) -> tuple[int, int]:
    relevant = [c for c in gateway.logged_calls if c.run_id == tag]
    return sum(c.tokens_in for c in relevant), sum(c.tokens_out for c in relevant)


async def run_fix(
    session: Any,
    gateway: ModelGateway,
    settings: Settings,
    candidate_id: int,
    repo: Path,
    hidden_check: HiddenCheck | None = None,
) -> FixAttempt:
    candidate = await session.get(FixCandidate, candidate_id)
    assert candidate is not None
    run = await session.get(Run, candidate.run_id)
    assert run is not None
    ticket = (
        await session.execute(select(Case).where(Case.source_key == run.ticket_key))
    ).scalar_one()
    pack, evidence_ids = await _evidence_pack(session, run.id)
    tag = f"{run.id}:fix"

    attempt_no = (
        await session.execute(
            select(func.count(FixAttempt.id)).where(
                FixAttempt.candidate_id == candidate_id
            )
        )
    ).scalar() or 0
    attempt_no += 1
    branch = f"fix/{ticket.source_key}-{attempt_no}"
    attempt = FixAttempt(candidate_id=candidate_id, attempt_no=attempt_no,
                         status="RUNNING", branch=branch, trace=[])
    session.add(attempt)
    await session.commit()
    candidate.status = "RUNNING"
    await session.commit()

    root = Path(settings.sandbox_root)
    if not root.is_absolute():
        root = Path("issue-intel") / root if Path("issue-intel").exists() else root
    sandbox = await create_sandbox(repo, root, branch, base="main")
    tools = Tools(sandbox.path, frozenset(settings.fix_allowlist), pack)
    trace: list[dict[str, Any]] = []

    def _record(step: dict[str, Any]) -> None:
        trace.append(step)

    try:
        baseline = await tools.run_tests()
        baseline_failing = {f.name for f in baseline.failing}
        hidden_before = await hidden_check(sandbox.path) if hidden_check else None
        _record({"cycle": 0, "step": "baseline", "passed": baseline.passed,
                 "failed": baseline.failed,
                 "hidden_passing": hidden_before})
        attempt.test_output = baseline.raw[-4000:]
        await session.commit()

        for cycle in range(1, settings.fix_max_cycles + 1):
            tin, tout = _spent(gateway, tag)
            if tin + tout >= settings.fix_token_budget:
                _record({"cycle": cycle, "step": "budget_exhausted"})
                break
            plan_result = await gateway.complete(
                TaskType.FIX_PLAN, system=PLAN_SYSTEM,
                user=f"Ticket {ticket.source_key}: {ticket.title}",
                data={"evidence": pack, "failures": attempt.test_output[-2000:]},
                run_id=tag,
            )
            try:
                plan = json.loads(plan_result.text)
                reads = [str(r) for r in plan.get("reads", [])]
            except ValueError:
                _record({"cycle": cycle, "step": "plan_unparseable"})
                continue
            contents: dict[str, str] = {}
            for rel in reads:
                try:
                    contents[rel] = tools.read_file(rel)
                    _record({"cycle": cycle, "step": "read", "file": rel})
                except ToolError as exc:
                    _record({"cycle": cycle, "step": "read_rejected",
                             "file": rel, "error": str(exc)})
            patch_result = await gateway.complete(
                TaskType.FIX_PATCH, system=PATCH_SYSTEM,
                user=f"Approach: {plan.get('approach', '')}",
                data={"files": json.dumps(contents)[:12000]}, run_id=tag,
            )
            try:
                patch_payload = json.loads(patch_result.text)
                patch_text = str(patch_payload.get("patch", ""))
            except ValueError:
                _record({"cycle": cycle, "step": "patch_unparseable"})
                continue
            try:
                message = await tools.apply_patch(patch_text)
            except ToolError as exc:
                _record({"cycle": cycle, "step": "patch_rejected",
                         "error": str(exc)})
                continue
            _record({"cycle": cycle, "step": "patch_applied", "detail": message})
            build = await tools.run_build()
            attempt.build_output = build.raw[-4000:]
            if not build.ok:
                _record({"cycle": cycle, "step": "build_failed"})
                attempt.test_output = build.raw[-4000:]
                await session.commit()
                continue
            tested: GateResult = await tools.run_tests()
            attempt.test_output = tested.raw[-4000:]
            await session.commit()
            now_failing = {f.name for f in tested.failing}
            fixed_before = bool(baseline_failing - now_failing)
            hidden_after = await hidden_check(sandbox.path) if hidden_check else None
            hidden_flipped = hidden_before is False and hidden_after is True
            _record({"cycle": cycle, "step": "tested", "passed": tested.passed,
                     "failed": tested.failed, "fixed_before": fixed_before,
                     "hidden_flipped": hidden_flipped})
            broke = bool(now_failing - baseline_failing)
            improved = fixed_before or hidden_flipped or (
                hidden_check is None and not baseline_failing
            )
            if tested.failed == 0 and not broke and improved:
                await _offer(session, sandbox_path=sandbox.path, branch=branch,
                             candidate=candidate, attempt=attempt, ticket_key=ticket.source_key,
                             explanation=str(patch_payload.get("explanation", "")),
                             evidence_ids=evidence_ids, tested=tested, trace=trace,
                             gateway=gateway, tag=tag)
                return attempt
        attempt.status = "GAVE_UP"
        candidate.status = "GAVE_UP"
        attempt.trace = trace
        tin, tout = _spent(gateway, tag)
        attempt.tokens_in, attempt.tokens_out = tin, tout
        await session.commit()
        return attempt
    finally:
        await remove_sandbox(repo, sandbox)


async def _offer(
    session: Any, sandbox_path: Path, branch: str, candidate: FixCandidate,
    attempt: FixAttempt, ticket_key: str, explanation: str,
    evidence_ids: list[str], tested: GateResult, trace: list[dict[str, Any]],
    gateway: ModelGateway, tag: str,
) -> None:
    await run_cmd(["git", "add", "-A"], cwd=sandbox_path, timeout_s=60)
    await run_cmd(["git", "commit", "-m", f"Fix {ticket_key}\n\n{explanation}"],
                  cwd=sandbox_path, timeout_s=60)
    sha = await run_cmd(["git", "rev-parse", "HEAD"], cwd=sandbox_path, timeout_s=60)
    diff = await run_cmd(["git", "diff", "main...HEAD"], cwd=sandbox_path, timeout_s=60)
    tin, tout = _spent(gateway, tag)
    attempt.status = "OFFERED"
    attempt.trace = trace
    attempt.tokens_in, attempt.tokens_out = tin, tout
    await session.flush()
    session.add(
        FixPr(attempt_id=attempt.id, kind="FIX", branch=branch, base="main",
              title=f"Fix {ticket_key}", root_cause=explanation,
              citations=evidence_ids,
              risk_note=f"{explanation[:300]} Tests: {tested.passed} passed.",
              test_results={"passed": tested.passed, "failed": tested.failed,
                            "commit": sha.stdout.strip()},
              diff=diff.stdout[-20000:], status="OPEN")
    )
    candidate.status = "OFFERED"
    await session.commit()
