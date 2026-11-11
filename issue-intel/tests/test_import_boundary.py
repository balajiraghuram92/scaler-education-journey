"""Import boundary: app/ must never touch eval ground truth or hidden fix cases."""
from __future__ import annotations

import ast
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent / "app"
FORBIDDEN = ("ground_truth", "fix_cases")


def test_app_never_imports_or_reads_ground_truth() -> None:
    violations: list[str] = []
    for path in sorted(APP_ROOT.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                dotted = node.module
                if any(token in dotted for token in FORBIDDEN):
                    violations.append(f"{path}:{node.lineno}: from-import {dotted}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if any(token in alias.name for token in FORBIDDEN):
                        violations.append(f"{path}:{node.lineno}: import {alias.name}")
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                if any(token in node.value for token in FORBIDDEN):
                    violations.append(f"{path}:{node.lineno}: string literal {node.value!r}")
    assert violations == [], "\n".join(violations)
