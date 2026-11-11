"""Ported from api/Data/PythonCurriculumSeedData.cs.

Seeds the Python Engineering course from files under Data/Content/python.
The file format and update rules are described on content_curriculum_seed_data.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from .content_curriculum_seed_data import resolve_content_root as _resolve
from .content_curriculum_seed_data import seed as _seed_folder


async def seed(session: AsyncSession, content_root: str | None = None) -> None:
    root = content_root or resolve_content_root()
    if root is None:
        print("[WARN] Python curriculum content folder (Data/Content/python) was not found. Skipping Python seeding.")
        return
    await _seed_folder(session, root)


def resolve_content_root() -> str | None:
    return _resolve("python")
