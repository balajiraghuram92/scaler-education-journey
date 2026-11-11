"""Gate: dotnet build + dotnet test in the worktree, with timeouts."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from app.agents.sandbox import run_cmd

SUMMARY_RE = re.compile(r"Failed:\s*(\d+).*?Passed:\s*(\d+)", re.IGNORECASE)
FAILED_RE = re.compile(r"^Failed (\S+)", re.MULTILINE)


@dataclass
class FailingTest:
    name: str
    message: str


@dataclass
class GateResult:
    ok: bool
    passed: int = 0
    failed: int = 0
    failing: list[FailingTest] = field(default_factory=list)
    raw: str = ""


def parse_dotnet_test(output: str) -> GateResult:
    match = SUMMARY_RE.search(output)
    failed = int(match.group(1)) if match else 0
    passed = int(match.group(2)) if match else 0
    failing: list[FailingTest] = []
    for name in FAILED_RE.findall(output):
        message = ""
        marker = f"Failed {name}"
        idx = output.find(marker)
        if idx >= 0:
            message = output[idx : idx + 400].splitlines()[0]
        failing.append(FailingTest(name=name, message=message))
    if match is None and failing:
        failed = len(failing)
    return GateResult(ok=failed == 0 and match is not None, passed=passed,
                      failed=failed, failing=failing, raw=output[-4000:])


async def dotnet_build(worktree: Path, timeout_s: float = 300.0) -> GateResult:
    result = await run_cmd(["dotnet", "build", "--nologo", "-v", "q"],
                           cwd=worktree, timeout_s=timeout_s)
    combined = (result.stdout + "\n" + result.stderr)[-4000:]
    return GateResult(ok=result.returncode == 0, raw=combined)


async def dotnet_test(worktree: Path, timeout_s: float = 600.0,
                      extra_args: list[str] | None = None) -> GateResult:
    cmd = ["dotnet", "test", "--nologo"]
    if extra_args:
        cmd.extend(extra_args)
    result = await run_cmd(cmd, cwd=worktree, timeout_s=timeout_s)
    parsed = parse_dotnet_test(result.stdout + "\n" + result.stderr)
    parsed.ok = parsed.ok and result.returncode == 0
    return parsed
