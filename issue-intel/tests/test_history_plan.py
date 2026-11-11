"""History-plan consistency: setup-history PLAN matches bugs.json and the tree."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX_CASES = ROOT / "evals" / "fix_cases"


def _load_plan() -> list[dict]:
    spec = importlib.util.spec_from_file_location(
        "setup_history", ROOT / "sample_repo" / "setup-history.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.PLAN


def test_plan_bugs_match_manifest_and_files() -> None:
    plan = [p for p in _load_plan() if p["kind"] == "bug"]
    manifest = json.loads((FIX_CASES / "bugs.json").read_text(encoding="utf-8"))
    by_id = {b["id"]: b for b in manifest["bugs"]}
    assert len(plan) == 12
    assert len(manifest["bugs"]) == 12
    for entry in plan:
        bug = by_id[entry["bug"]]
        assert bug["symptom"] == entry["symptom"]
        assert bug["files"] == entry["files"]
        for rel in bug["files"]:
            assert (ROOT / "sample_repo" / rel).exists(), rel
        assert (FIX_CASES / bug["patch"]).exists()
    assert (FIX_CASES / "HiddenTests.cs").exists()


def test_out_of_scope_bugs_are_assetimport_only() -> None:
    manifest = json.loads((FIX_CASES / "bugs.json").read_text(encoding="utf-8"))
    out = [b for b in manifest["bugs"] if b["scope"] == "out"]
    assert len(out) == 2
    assert all(b["module"] == "AssetImport" for b in out)


def test_two_file_and_two_commit_counts() -> None:
    manifest = json.loads((FIX_CASES / "bugs.json").read_text(encoding="utf-8"))
    two_file = [b for b in manifest["bugs"] if len(b["files"]) == 2]
    assert len(two_file) == 4  # bug09, bug10, bug11, bug12
    two_commit = [b for b in manifest["bugs"] if b.get("two_commit")]
    assert [b["id"] for b in two_commit] == ["bug12"]
