"""The seven fix-agent tools. Path validation on every call.

Reads: any path inside the worktree (absolute paths, `..` and symlinks that
escape are rejected). Writes: only `src/<Module>/...` for allow-listed
modules. There is no shell tool and no network tool.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from app.agents.gate import GateResult, dotnet_build, dotnet_test


class ToolError(Exception):
    pass


PATCH_FILE_RE = re.compile(r"^\+\+\+ b/(.+)$")


def patch_files(patch_text: str) -> list[str]:
    """Files touched by a unified diff (its `+++ b/...` lines)."""
    return [
        m.group(1)
        for line in patch_text.splitlines()
        if (m := PATCH_FILE_RE.match(line))
    ]


@dataclass
class Tools:
    worktree: Path
    allowlist: frozenset[str]
    _evidence_pack: str = ""

    def _resolve(self, rel: str, for_write: bool = False) -> Path:
        candidate = Path(rel)
        if candidate.is_absolute():
            raise ToolError(f"absolute path rejected: {rel}")
        if ".." in candidate.parts:
            raise ToolError(f"parent traversal rejected: {rel}")
        target = (self.worktree / candidate).resolve()
        if target != self.worktree.resolve() and self.worktree.resolve() not in target.parents:
            raise ToolError(f"path escapes worktree: {rel}")
        if for_write:
            parts = target.relative_to(self.worktree.resolve()).parts
            if len(parts) < 3 or parts[0] != "src" or parts[1] not in self.allowlist:
                raise ToolError(f"write outside allow-list rejected: {rel}")
        return target

    def list_files(self, rel: str = "") -> list[str]:
        root = self._resolve(rel or ".")
        if not root.is_dir():
            raise ToolError(f"not a directory: {rel}")
        return sorted(
            str(p.relative_to(self.worktree.resolve()))
            for p in root.iterdir()
        )

    def read_file(self, rel: str) -> str:
        target = self._resolve(rel)
        if not target.is_file():
            raise ToolError(f"not a file: {rel}")
        return target.read_text(encoding="utf-8")

    def search_text(self, pattern: str, rel: str = "") -> list[dict[str, str]]:
        root = self._resolve(rel or ".")
        try:
            compiled = re.compile(pattern)
        except re.error as exc:
            raise ToolError(f"bad pattern: {exc}") from exc
        hits: list[dict[str, str]] = []
        roots = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
        for path in roots:
            if len(hits) >= 100:
                break
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for lineno, line in enumerate(text.splitlines(), start=1):
                if compiled.search(line):
                    hits.append({
                        "file": str(path.relative_to(self.worktree.resolve())),
                        "line": str(lineno), "text": line[:200],
                    })
                    if len(hits) >= 100:
                        break
        return hits

    async def apply_patch(self, patch_text: str) -> str:
        touched = patch_files(patch_text)
        if not touched:
            raise ToolError("patch touches no files")
        for rel in touched:
            self._resolve(rel, for_write=True)
        proc_input = patch_text.encode()
        import asyncio

        proc = await asyncio.create_subprocess_exec(
            "git", "apply", "-", cwd=str(self.worktree),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        out, err = await proc.communicate(proc_input)
        if proc.returncode != 0:
            raise ToolError(f"patch does not apply: {err.decode(errors='replace')[-500:]}")
        _ = out
        return f"applied, touched: {', '.join(touched)}"

    async def run_build(self) -> GateResult:
        return await dotnet_build(self.worktree)

    async def run_tests(self) -> GateResult:
        return await dotnet_test(self.worktree)

    def read_evidence(self) -> str:
        return self._evidence_pack
