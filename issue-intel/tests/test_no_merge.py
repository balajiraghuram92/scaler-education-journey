"""No-merge tests: the agent has no integration capability."""
from __future__ import annotations

import re
from pathlib import Path

from app.agents.tools import Tools

AGENTS_ROOT = Path(__file__).resolve().parent.parent / "app" / "agents"
EXPECTED_TOOLS = {
    "list_files", "read_file", "search_text", "apply_patch",
    "run_build", "run_tests", "read_evidence",
}
FORBIDDEN = re.compile(r"\bmerge\b|\bpush\b", re.IGNORECASE)


def test_tools_are_exactly_the_seven() -> None:
    methods = {m for m in dir(Tools) if not m.startswith("_")}
    assert methods == EXPECTED_TOOLS


def test_no_merge_or_push_anywhere_in_agents() -> None:
    violations = []
    for path in sorted(AGENTS_ROOT.glob("*.py")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if FORBIDDEN.search(line):
                violations.append(f"{path.name}:{lineno}: {line.strip()}")
    assert violations == [], "\n".join(violations)
