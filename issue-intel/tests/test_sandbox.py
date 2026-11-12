"""create_sandbox resolves a relative root (needs git; no DB)."""

from __future__ import annotations

import asyncio
import shutil
import subprocess
from pathlib import Path

import pytest

from app.agents.sandbox import create_sandbox, remove_sandbox

needs_git = pytest.mark.skipif(
    shutil.which("git") is None, reason="git not on PATH"
)


@needs_git
def test_create_sandbox_returns_absolute_existing_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=repo, check=True
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "--allow-empty", "-m", "init"], cwd=repo, check=True)

    async def _run() -> None:
        sandbox = await create_sandbox(repo, Path("sandboxes"), "fix-x", base="main")
        assert sandbox.path.is_absolute()
        assert sandbox.path.exists()
        await remove_sandbox(repo, sandbox)
        assert not sandbox.path.exists()

    asyncio.run(_run())
