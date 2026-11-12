"""Sandbox: a fresh git worktree of sample_repo per attempt.

Worktrees live under the sandbox root and are removed when the attempt ends.
All subprocess calls go through run_cmd (no shell, timeouts enforced).
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CmdResult:
    returncode: int
    stdout: str
    stderr: str


async def run_cmd(cmd: list[str], cwd: Path, timeout_s: float) -> CmdResult:
    proc = await asyncio.create_subprocess_exec(
        *cmd, cwd=str(cwd),
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout_s)
    except TimeoutError:
        proc.kill()
        out, err = await proc.communicate()
        return CmdResult(
            124, out.decode(errors="replace"),
            f"timeout: {err.decode(errors='replace')}",
        )
    code = proc.returncode if proc.returncode is not None else 1
    return CmdResult(code, out.decode(errors="replace"), err.decode(errors="replace"))


@dataclass
class Sandbox:
    path: Path
    branch: str


async def create_sandbox(repo: Path, root: Path, branch: str, base: str = "main") -> Sandbox:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    path = root / branch.replace("/", "-")
    result = await run_cmd(
        ["git", "worktree", "add", "-b", branch, str(path), base], cwd=repo, timeout_s=120
    )
    if result.returncode != 0:
        raise RuntimeError(f"worktree add failed: {result.stderr[-500:]}")
    return Sandbox(path=path, branch=branch)


async def remove_sandbox(repo: Path, sandbox: Sandbox) -> None:
    await run_cmd(
        ["git", "worktree", "remove", "--force", str(sandbox.path)],
        cwd=repo, timeout_s=120,
    )
