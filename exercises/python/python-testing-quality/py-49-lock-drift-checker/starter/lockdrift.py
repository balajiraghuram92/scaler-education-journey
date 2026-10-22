from __future__ import annotations

from typing import Literal


def normalize(name: str) -> str:
    """PEP 503 name normalisation (lowercase, runs of ``-``, ``_``, ``.`` become ``-``)."""
    raise NotImplementedError("Implement normalize")


def parse_release(version: str) -> tuple[int, ...]:
    """``"1.2.3"`` -> ``(1, 2, 3)``. Anything that is not dotted integers
    (``1.0rc1``, ``1.0.post1``, ``v1.0``, empty) raises ``ValueError``."""
    raise NotImplementedError("Implement parse_release")


def satisfies(version: str, specifier: str) -> bool:
    """Check a comma-separated specifier such as ``">=0.27,<1"`` or ``"~=2.8"``.

    Supports ``==  !=  >=  <=  >  <  ~=``. Versions of different length compare as if
    zero-padded (``1.2 == 1.2.0``); compare numerically (``0.10.0 > 0.9``).
    ``~=2.8`` means ``>=2.8`` with the same first component; ``~=2.8.1`` means ``>=2.8.1``
    with the same first two. An empty specifier accepts everything; an unknown clause
    raises ``ValueError("unsupported specifier clause ...")``.
    """
    raise NotImplementedError("Implement satisfies")


def split_requirement(requirement: str) -> tuple[str, str]:
    """``"Pydantic[email]~=2.8"`` -> ``("pydantic", "~=2.8")``.
    Extras and environment markers (``; sys_platform != "win32"``) are discarded."""
    raise NotImplementedError("Implement split_requirement")


def find_drift(pyproject_text: str, lock_text: str) -> list[str]:
    """Compare requirements with a uv-style lock file (use ``tomllib``).

    Collect string requirements from ``project.dependencies`` and every
    ``[dependency-groups]`` list (skip non-string items such as ``{include-group = ...}``),
    look each name up in the lock's ``[[package]]`` tables (``name``, ``version``) and
    return a sorted list of ``"<name>: missing from lock"`` or
    ``"<name>: locked <version> violates '<specifier>'"``.
    """
    raise NotImplementedError("Implement find_drift")


def bump(version: str, part: Literal["major", "minor", "patch"]) -> str:
    """SemVer bump: ``bump("1.4.9", "minor") == "1.5.0"`` (lower parts reset to 0)."""
    raise NotImplementedError("Implement bump")
