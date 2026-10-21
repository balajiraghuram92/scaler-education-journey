from __future__ import annotations

import re
import tomllib
from typing import Literal

_RELEASE_RE = re.compile(r"^\d+(\.\d+)*$")
_CLAUSE_RE = re.compile(r"^(==|!=|>=|<=|~=|>|<)\s*(\d+(?:\.\d+)*)$")
_REQ_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*([^;]*)")


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_release(version: str) -> tuple[int, ...]:
    """Numeric releases only ('1.2.3'); pre/post/dev releases raise ValueError."""
    if not _RELEASE_RE.match(version):
        raise ValueError(f"unsupported version: {version!r}")
    return tuple(int(part) for part in version.split("."))


def _cmp(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    width = max(len(a), len(b))
    pa = a + (0,) * (width - len(a))
    pb = b + (0,) * (width - len(b))
    return (pa > pb) - (pa < pb)


def satisfies(version: str, specifier: str) -> bool:
    """Check a comma-separated specifier such as '>=0.27,<1' or '~=2.8'."""
    current = parse_release(version)
    for raw in filter(None, (c.strip() for c in specifier.split(","))):
        match = _CLAUSE_RE.match(raw)
        if match is None:
            raise ValueError(f"unsupported specifier clause: {raw!r}")
        op, target_text = match.groups()
        target = parse_release(target_text)
        order = _cmp(current, target)
        if op == "==":
            ok = order == 0
        elif op == "!=":
            ok = order != 0
        elif op == ">=":
            ok = order >= 0
        elif op == "<=":
            ok = order <= 0
        elif op == ">":
            ok = order > 0
        elif op == "<":
            ok = order < 0
        else:  # '~=' : >= target and same prefix of all but the last component
            if len(target) < 2:
                raise ValueError("~= needs at least two components")
            prefix = target[:-1]
            ok = order >= 0 and current[: len(prefix)] == prefix
        if not ok:
            return False
    return True


def split_requirement(requirement: str) -> tuple[str, str]:
    match = _REQ_RE.match(requirement)
    if match is None:
        raise ValueError(f"invalid requirement: {requirement!r}")
    return normalize(match.group(1)), match.group(2).strip()


def find_drift(pyproject_text: str, lock_text: str) -> list[str]:
    """Return human-readable drift problems between pyproject.toml and uv.lock."""
    project = tomllib.loads(pyproject_text)
    locked: dict[str, str] = {
        normalize(pkg["name"]): pkg["version"]
        for pkg in tomllib.loads(lock_text).get("package", [])
    }
    requirements: list[str] = list(project.get("project", {}).get("dependencies", []))
    for group in project.get("dependency-groups", {}).values():
        requirements.extend(item for item in group if isinstance(item, str))

    problems: list[str] = []
    for requirement in requirements:
        name, specifier = split_requirement(requirement)
        version = locked.get(name)
        if version is None:
            problems.append(f"{name}: missing from lock")
        elif not satisfies(version, specifier):
            problems.append(f"{name}: locked {version} violates '{specifier}'")
    return sorted(problems)


def bump(version: str, part: Literal["major", "minor", "patch"]) -> str:
    major, minor, patch = parse_release(version)
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"
