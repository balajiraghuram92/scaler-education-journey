from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEV_TOOLS = frozenset({"pytest", "ruff", "mypy", "pyright", "black", "flake8", "isort"})


# TODO: make Issue frozen and orderable (sorting by code, then message).
@dataclass
class Issue:
    code: str
    message: str


def normalize(name: str) -> str:
    """PEP 503 normalisation: lowercase, runs of ``-``, ``_``, ``.`` become one ``-``."""
    raise NotImplementedError("Implement normalize")


def requirement_name(requirement: str) -> str:
    """Normalised distribution name from a requirement string such as
    ``"PyTest[extra]>=8; python_version >= '3.12'"``. Raise ``ValueError`` if there is no name."""
    raise NotImplementedError("Implement requirement_name")


def audit(root: Path) -> list[Issue]:
    """Audit the project in ``root`` and return issues sorted by code.

    PP001 pyproject.toml not found (return only this issue)
    PP002 no [build-system] table
    PP003 project.requires-python missing
    PP004 a dev tool is in project.dependencies (one issue per occurrence)
    PP005 version is both static and listed in ``dynamic``
    PP006 version is neither static nor dynamic
    PP007 a [project.scripts] target is not ``module.path:function``
    PP008 src/<name with - replaced by _>/__init__.py does not exist

    Invalid TOML must propagate ``tomllib.TOMLDecodeError``.
    """
    raise NotImplementedError("Implement audit")
