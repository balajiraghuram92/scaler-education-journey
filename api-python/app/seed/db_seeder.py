"""Ported from api/Data/DbSeeder.cs."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.study_task import StudyTask
from ..models.study_vertical import StudyVertical
from . import (
    chapter_seed_data,
    content_curriculum_seed_data,
    fde_curriculum_seed_data,
    fde_seed_data,
    java_vertical_seed_data,
    knowledge_atlas_seed_data,
    localization_seed_data,
    mcq_migration_seed_data,
    python_curriculum_seed_data,
    reading_map_seed_data,
)


async def _get_or_create_vertical(
    session: AsyncSession, name: str, description: str
) -> StudyVertical:
    vertical = (
        await session.execute(select(StudyVertical).where(StudyVertical.name == name))
    ).scalar_one_or_none()
    if vertical is None:
        vertical = StudyVertical(
            name=name, description=description, updated_at=datetime.now(timezone.utc)
        )
        session.add(vertical)
        await session.flush()
    return vertical


async def initialize(session: AsyncSession) -> None:
    # 1. FDE Vertical
    fde_vertical = await _get_or_create_vertical(
        session, "FDE", "Full-Stack Data Engineering Journey"
    )
    has_tasks = (
        await session.execute(
            select(StudyTask.id).where(StudyTask.vertical_id == fde_vertical.id).limit(1)
        )
    ).first()
    if has_tasks is None:
        for task in fde_seed_data.get_tasks():
            task.vertical_id = fde_vertical.id
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
        await session.flush()

    # 2. Java Vertical
    await java_vertical_seed_data.seed(session)

    # 3. FDE Curriculum (must run before knowledge atlas/reading map)
    await fde_curriculum_seed_data.seed(session)

    # 4. Knowledge Atlas & Reading Map
    await knowledge_atlas_seed_data.seed(session)
    await reading_map_seed_data.seed(session)

    # 5. Chapter Content (code comparisons, diagrams, notes)
    await chapter_seed_data.seed(session)

    # 6. Python Course (file-driven under Data/Content/python)
    await python_curriculum_seed_data.seed(session)

    # 7. AI Infusion & AWS Bootcamp (file-driven under Data/Content/{ai-infusion,aws-bootcamp})
    for folder in ("ai-infusion", "aws-bootcamp"):
        if content_curriculum_seed_data.resolve_content_root(folder) is not None:
            await content_curriculum_seed_data.seed_folder(session, folder)

    # 8. Localization Lab
    await localization_seed_data.seed(session)

    # 9. MCQ dynamic tables from mcq-migration-data.json
    await mcq_migration_seed_data.seed(session)

    await session.commit()
    print("Database seeding completed successfully.")
