"""Tool validation tests, including hostile inputs (no DB)."""
from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

import pytest

from app.agents.tools import ToolError, Tools, patch_files

PATCH_OK = """diff --git a/src/VersionControl/ok.cs b/src/VersionControl/ok.cs
--- a/src/VersionControl/ok.cs
+++ b/src/VersionControl/ok.cs
@@ -1 +1 @@
-hello
+world
"""

PATCH_OUTSIDE = """diff --git a/src/AssetImport/out.cs b/src/AssetImport/out.cs
--- a/src/AssetImport/out.cs
+++ b/src/AssetImport/out.cs
@@ -1 +1 @@
-hello
+world
"""


def _tools(tmp_path: Path) -> Tools:
    (tmp_path / "src" / "VersionControl").mkdir(parents=True)
    (tmp_path / "src" / "AssetImport").mkdir(parents=True)
    (tmp_path / "src" / "VersionControl" / "ok.cs").write_text("hello\n")
    (tmp_path / "src" / "AssetImport" / "out.cs").write_text("hello\n")
    return Tools(tmp_path, frozenset({"VersionControl"}))


def test_read_list_search_happy_paths(tmp_path: Path) -> None:
    tools = _tools(tmp_path)
    assert "src" in tools.list_files("")
    assert tools.read_file("src/VersionControl/ok.cs") == "hello\n"
    hits = tools.search_text("hello")
    assert {h["file"] for h in hits} == {
        "src/VersionControl/ok.cs", "src/AssetImport/out.cs",
    }


def test_absolute_paths_rejected(tmp_path: Path) -> None:
    tools = _tools(tmp_path)
    with pytest.raises(ToolError):
        tools.read_file(str(tmp_path / "src" / "VersionControl" / "ok.cs"))
    with pytest.raises(ToolError):
        tools.list_files("/etc")


def test_parent_traversal_rejected(tmp_path: Path) -> None:
    tools = _tools(tmp_path)
    for rel in ("../ok.cs", "src/../../ok.cs", "src/VersionControl/../../../x"):
        with pytest.raises(ToolError):
            tools.read_file(rel)


def test_symlink_escape_rejected(tmp_path: Path) -> None:
    outside = tmp_path.parent / "escape-target.txt"
    outside.write_text("secret", encoding="utf-8")
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(outside)
    except OSError:
        pytest.skip("symlinks need privileges on this machine")
    tools = _tools(tmp_path)
    with pytest.raises(ToolError):
        tools.read_file("link.txt")


def test_patch_files_parsed() -> None:
    assert patch_files(PATCH_OK) == ["src/VersionControl/ok.cs"]
    assert patch_files("no diff here") == []


def test_apply_patch_outside_allowlist_rejected_without_git(tmp_path: Path) -> None:
    tools = _tools(tmp_path)
    with pytest.raises(ToolError):
        asyncio.run(tools.apply_patch(PATCH_OUTSIDE))
    with pytest.raises(ToolError):
        asyncio.run(tools.apply_patch("no diff here"))


def test_apply_patch_roundtrip_needs_git(tmp_path: Path) -> None:
    if shutil.which("git") is None:
        pytest.skip("git binary required")
    tools = _tools(tmp_path)
    message = asyncio.run(tools.apply_patch(PATCH_OK))
    assert "src/VersionControl/ok.cs" in message
    assert (tmp_path / "src" / "VersionControl" / "ok.cs").read_text() == "world\n"
    with pytest.raises(ToolError):
        asyncio.run(tools.apply_patch(PATCH_OK))  # no longer applies


def test_bad_pattern_rejected(tmp_path: Path) -> None:
    tools = _tools(tmp_path)
    with pytest.raises(ToolError):
        tools.search_text("(unclosed")
