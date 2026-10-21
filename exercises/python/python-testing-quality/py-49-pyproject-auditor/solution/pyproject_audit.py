from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

DEV_TOOLS = frozenset({"pytest", "ruff", "mypy", "pyright", "black", "flake8", "isort"})
_NAME_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")
_ENTRY_RE = re.compile(r"^[A-Za-z_][\w.]*:[A-Za-z_]\w*$")


@dataclass(frozen=True, order=True)
class Issue:
    code: str
    message: str


def normalize(name: str) -> str:
    """PEP 503 name normalisation."""
    return re.sub(r"[-_.]+", "-", name).lower()


def requirement_name(requirement: str) -> str:
    match = _NAME_RE.match(requirement)
    if match is None:
        raise ValueError(f"invalid requirement: {requirement!r}")
    return normalize(match.group(1))


def audit(root: Path) -> list[Issue]:
    path = root / "pyproject.toml"
    if not path.is_file():
        return [Issue("PP001", "pyproject.toml not found")]
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    issues: list[Issue] = []

    if "build-system" not in data:
        issues.append(Issue("PP002", "missing [build-system]"))

    project = data.get("project", {})
    if "requires-python" not in project:
        issues.append(Issue("PP003", "project.requires-python is not set"))

    for requirement in project.get("dependencies", []):
        if requirement_name(requirement) in DEV_TOOLS:
            issues.append(
                Issue("PP004", f"dev tool in runtime dependencies: {requirement}")
            )

    dynamic = project.get("dynamic", [])
    has_static = "version" in project
    if has_static and "version" in dynamic:
        issues.append(Issue("PP005", "version is both static and dynamic"))
    if not has_static and "version" not in dynamic:
        issues.append(Issue("PP006", "version is neither static nor dynamic"))

    for script, target in project.get("scripts", {}).items():
        if not _ENTRY_RE.match(target):
            issues.append(Issue("PP007", f"script {script!r} must be 'module:function'"))

    name = project.get("name")
    if name is not None:
        package = normalize(name).replace("-", "_")
        if not (root / "src" / package / "__init__.py").is_file():
            issues.append(Issue("PP008", f"expected src/{package}/__init__.py (src layout)"))

    return sorted(issues)
