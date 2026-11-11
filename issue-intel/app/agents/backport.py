"""Backport agent: cherry-pick an integrated fix onto release branches.

One PR record per branch. Only textual conflicts in allow-listed files are
resolved (with the conflict_resolve task); anything else blocks that branch.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.agents.sandbox import create_sandbox, remove_sandbox, run_cmd
from app.agents.tools import ToolError, Tools
from app.gateway.gateway import ModelGateway
from app.gateway.tasks import TaskType
from app.models.g3 import FixAttempt, FixPr
from app.settings import Settings

CONFLICT_SYSTEM = (
    "Resolve the textual conflict. Reply with JSON only: "
    '{"patch": "unified diff from the repo root removing the conflict '
    'markers", "explanation": "..."}.'
)


async def backport_pr(
    session: Any, gateway: ModelGateway, settings: Settings,
    pr_id: int, branches: list[str], repo: Path,
) -> list[FixPr]:
    pr = await session.get(FixPr, pr_id)
    assert pr is not None
    commit = str(pr.test_results.get("commit", ""))
    if not commit:
        raise ValueError("fix PR has no recorded commit")
    root = Path(settings.sandbox_root)
    if not root.is_absolute():
        root = Path("issue-intel") / root if Path("issue-intel").exists() else root
    made: list[FixPr] = []
    for base in branches:
        bp_branch = f"backport/{pr.branch}-{base}".replace("/", "-")
        sandbox = await create_sandbox(repo, root, bp_branch, base=base)
        tools = Tools(sandbox.path, frozenset(settings.fix_allowlist))
        try:
            picked = await run_cmd(["git", "cherry-pick", commit],
                                   cwd=sandbox.path, timeout_s=120)
            if picked.returncode != 0:
                conflicted = await run_cmd(
                    ["git", "diff", "--name-only", "--diff-filter=U"],
                    cwd=sandbox.path, timeout_s=60,
                )
                files = [f for f in conflicted.stdout.split() if f]
                outside = [
                    f for f in files
                    if not (f.startswith("src/")
                            and f.split("/")[1] in settings.fix_allowlist)
                ]
                if outside:
                    await run_cmd(["git", "cherry-pick", "--abort"],
                                  cwd=sandbox.path, timeout_s=60)
                    made.append(await _record(
                        session, pr, bp_branch, base, "BLOCKED",
                        {"reason": f"conflict outside allow-list: {outside}"}, ""))
                    continue
                hunks = {f: tools.read_file(f) for f in files}
                result = await gateway.complete(
                    TaskType.CONFLICT_RESOLVE, system=CONFLICT_SYSTEM,
                    user=f"Backport {pr.branch} onto {base}",
                    data={"conflicts": json.dumps(hunks)[:12000]},
                )
                try:
                    patch_text = str(json.loads(result.text).get("patch", ""))
                    await tools.apply_patch(patch_text)
                except (ValueError, ToolError) as exc:
                    await run_cmd(["git", "cherry-pick", "--abort"],
                                  cwd=sandbox.path, timeout_s=60)
                    made.append(await _record(
                        session, pr, bp_branch, base, "BLOCKED",
                        {"reason": f"unresolvable conflict: {exc}"}, ""))
                    continue
                cont = await run_cmd(
                    ["git", "-c", "core.editor=true", "cherry-pick", "--continue"],
                    cwd=sandbox.path, timeout_s=120,
                )
                if cont.returncode != 0:
                    await run_cmd(["git", "cherry-pick", "--abort"],
                                  cwd=sandbox.path, timeout_s=60)
                    made.append(await _record(
                        session, pr, bp_branch, base, "BLOCKED",
                        {"reason": "cherry-pick --continue failed"}, ""))
                    continue
            build = await tools.run_build()
            if not build.ok:
                made.append(await _record(
                    session, pr, bp_branch, base, "BLOCKED",
                    {"reason": "build failed", "output": build.raw[-2000:]}, ""))
                continue
            tested = await tools.run_tests()
            if tested.failed:
                made.append(await _record(
                    session, pr, bp_branch, base, "BLOCKED",
                    {"reason": "tests failed",
                     "failing": [f.name for f in tested.failing]}, ""))
                continue
            diff = await run_cmd(["git", "diff", f"{base}...HEAD"],
                                 cwd=sandbox.path, timeout_s=60)
            made.append(await _record(
                session, pr, bp_branch, base, "OPEN",
                {"passed": tested.passed, "failed": 0}, diff.stdout[-20000:]))
        finally:
            await remove_sandbox(repo, sandbox)
    return made


async def _record(
    session: Any, pr: FixPr, branch: str, base: str, status: str,
    test_results: dict[str, Any], diff: str,
) -> FixPr:
    attempt = await session.get(FixAttempt, pr.attempt_id)
    assert attempt is not None
    row = FixPr(
        attempt_id=attempt.id, kind="BACKPORT", branch=branch, base=base,
        title=f"Backport {pr.title} to {base}", root_cause=pr.root_cause,
        citations=list(pr.citations), risk_note=pr.risk_note,
        test_results=test_results, diff=diff, status=status,
    )
    session.add(row)
    await session.commit()
    return row
