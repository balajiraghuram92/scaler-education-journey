"""Build the sample_repo git history. Run once from issue-intel/sample_repo/.

NOT RUN in this track (shell unavailable). Expected commands are recorded in
issue-intel/PROGRESS.md.

Flow:
  1. git init -b main, commit the on-disk clean tree as the base.
  2. For each bug in PLAN: reverse-apply its reference fix patch
     (bug12 in two per-file commits: the interaction bug), commit with a
     Symptom: trailer so ingest can crosswalk text -> change.
  3. Branch release/2023.3 after bug04 and release/2024.3 after bug08, with two
     release-note commits each, then return to main.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX_CASES = HERE.parent / "evals" / "fix_cases"

# Single source of truth for the planned history. The synthetic generator and
# tests import PLAN from this file; never duplicate it.
PLAN: list[dict] = [
    {"seq": 0, "kind": "base", "message": "Initial import of Tessera Editor Tools"},
    {"seq": 1, "kind": "bug", "bug": "bug01", "symptom": "trailer-colon",
     "files": ["src/VersionControl/CommitParser.cs"]},
    {"seq": 2, "kind": "bug", "bug": "bug02", "symptom": "branch-dots",
     "files": ["src/VersionControl/BranchNameValidator.cs"]},
    {"seq": 3, "kind": "bug", "bug": "bug03", "symptom": "french-zero-plural",
     "files": ["src/Localization/PluralRules.cs"]},
    {"seq": 4, "kind": "bug", "bug": "bug04", "symptom": "skipped-parent-culture",
     "files": ["src/Localization/ResourceFallback.cs"]},
    {"seq": 5, "kind": "bug", "bug": "bug05", "symptom": "recent-files-duplicate",
     "files": ["src/UiState/RecentFiles.cs"]},
    {"seq": 6, "kind": "bug", "bug": "bug06", "symptom": "panel-width-lost",
     "files": ["src/UiState/LayoutSerializer.cs"]},
    {"seq": 7, "kind": "bug", "bug": "bug07", "symptom": "mipmap-off-by-one",
     "files": ["src/AssetImport/TextureScaler.cs"]},
    {"seq": 8, "kind": "bug", "bug": "bug08", "symptom": "normaliser-clipping",
     "files": ["src/AssetImport/AudioNormalizer.cs"]},
    {"seq": 9, "kind": "bug", "bug": "bug09", "symptom": "turkish-i-lookup",
     "files": ["src/Localization/CultureCode.cs", "src/Localization/ResourceLoader.cs"]},
    {"seq": 10, "kind": "bug", "bug": "bug10", "symptom": "root-ancestor-missed",
     "files": ["src/VersionControl/MergeBase.cs", "src/VersionControl/HistoryWalker.cs"]},
    {"seq": 11, "kind": "bug", "bug": "bug11", "symptom": "theme-never-restored",
     "files": ["src/UiState/ThemeManager.cs", "src/UiState/SettingsStore.cs"]},
    {"seq": 12, "kind": "bug", "bug": "bug12", "symptom": "cache-case-interaction",
     "files": ["src/VersionControl/HashUtil.cs", "src/VersionControl/CommitCache.cs"],
     "commits": 2},
]

RELEASE_BRANCHES = [
    {"branch": "release/2023.3", "after_seq": 4},
    {"branch": "release/2024.3", "after_seq": 8},
]


def run(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=HERE, check=True,
                            capture_output=True, text=True)
    return result.stdout.strip()


def main() -> None:
    run("init", "-b", "main")
    run("config", "user.name", "Tessera Sustained Engineering")
    run("config", "user.email", "se@tessera-engines.example")
    run("config", "commit.gpgsign", "false")
    run("add", "-A")
    run("commit", "-m", PLAN[0]["message"])
    by_seq: dict[int, str] = {0: run("rev-parse", "HEAD")}
    manifest = json.loads((FIX_CASES / "bugs.json").read_text(encoding="utf-8"))
    patches = {b["id"]: b["patch"] for b in manifest["bugs"]}

    for entry in PLAN[1:]:
        patch = FIX_CASES / patches[entry["bug"]]
        if entry.get("commits", 1) == 2:
            for i, rel in enumerate(entry["files"]):
                run("apply", "-R", f"--include={rel}", str(patch))
                run("add", "-A")
                run("commit", "-m",
                    f"Introduce defect ({entry['symptom']}) part {i + 1}\n\nSymptom: {entry['symptom']}")
        else:
            run("apply", "-R", str(patch))
            run("add", "-A")
            run("commit", "-m",
                f"Introduce defect ({entry['symptom']})\n\nSymptom: {entry['symptom']}")
        by_seq[entry["seq"]] = run("rev-parse", "HEAD")

    for spec in RELEASE_BRANCHES:
        run("checkout", "-b", spec["branch"], by_seq[spec["after_seq"]])
        notes = HERE / "docs" / f"relnotes-{spec['branch'].split('/')[1]}.md"
        notes.parent.mkdir(exist_ok=True)
        notes.write_text(f"# {spec['branch']} release notes\n", encoding="utf-8")
        run("add", "-A")
        run("commit", "-m", f"Add {spec['branch']} release notes")
        (notes.parent / f"changelog-{spec['branch'].split('/')[1]}.md").write_text(
            "# Changelog\n", encoding="utf-8")
        run("add", "-A")
        run("commit", "-m", f"Add {spec['branch']} changelog")
    run("checkout", "main")
    (HERE / ".history.json").write_text(json.dumps(by_seq, indent=2), encoding="utf-8")
    print("history built; HEAD:", run("rev-parse", "--short", "HEAD"))


if __name__ == "__main__":
    main()
