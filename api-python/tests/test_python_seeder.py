"""Seeder test from SessionAndLearnerStateTests.cs (PythonSeeder_*), translated in P7.

Uses an isolated content folder under tmp_path (never the real Data/Content tree).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import Course
from app.models.lesson import Lesson
from app.models.problem import Problem
from app.seed.python_curriculum_seed_data import seed as seed_python


def _write_course(root: Path) -> None:
    (root / "lessons").mkdir(parents=True)
    (root / "assignments").mkdir(parents=True)
    (root / "course.json").write_text(
        json.dumps(
            {
                "slug": "python-engineering",
                "title": "Python Engineering",
                "description": "d",
                "verticalName": "Python Engineering",
                "modules": [
                    {
                        "slug": "m1",
                        "title": "Module 1",
                        "description": "d",
                        "badge": "Module 1",
                        "lessons": [
                            {
                                "slug": "py-01",
                                "title": "One",
                                "description": "d",
                                "minutes": 70,
                                "difficulty": "Advanced",
                                "reference": "ref",
                            },
                            {
                                "slug": "py-02",
                                "title": "Two",
                                "description": "d",
                                "minutes": 15,
                                "difficulty": "Intermediate",
                                "reference": "ref",
                            },
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / "lessons" / "py-01.md").write_text(
        "# One\r\n\r\n## Concepts Covered\r\nBody\r\n", encoding="utf-8"
    )
    (root / "assignments" / "py-01.json").write_text(
        json.dumps(
            {
                "assignments": [
                    {
                        "slug": "p1",
                        "title": "Problem",
                        "problemStatement": "s",
                        "requirements": "r",
                        "referenceSolution": "y",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


@pytest.mark.asyncio
async def test_python_seeder_marks_draft_and_updates_status_on_file_change(
    scratch_session: AsyncSession, tmp_path: Path
) -> None:
    db = scratch_session
    root = tmp_path / "content"
    _write_course(root)
    await seed_python(db, str(root))

    lessons = (
        await db.execute(
            select(Lesson)
            .options(selectinload(Lesson.problems))
            .order_by(Lesson.order_index)
        )
    ).scalars().all()

    assert len(lessons) == 2
    assert lessons[0].slug == "py-01"
    assert lessons[0].content_status == "Draft"
    assert lessons[0].estimated_minutes == 70
    assert lessons[0].difficulty == "Advanced"
    assert lessons[0].horstmann_ref == "ref"
    assert "## Concepts Covered" in lessons[0].content_body
    assert lessons[1].content_status == "Outline"
    assert len(lessons[0].problems) == 1
    assert lessons[0].problems[0].language == "python"
    assert lessons[0].problems[0].run_command == "pytest -q"
    assert lessons[0].problems[0].reference_solution == "y"

    # A reviewed lesson keeps its status until the file actually changes.
    published_lesson_id = lessons[0].id
    published = await db.get(Lesson, published_lesson_id)
    assert published is not None
    published.content_status = "Published"
    await seed_python(db, str(root))
    still_published = await db.get(Lesson, published_lesson_id)
    assert still_published is not None
    assert still_published.content_status == "Published"

    (root / "lessons" / "py-01.md").write_text("# One\r\n\r\nRevised\r\n", encoding="utf-8")
    await seed_python(db, str(root))
    revised = await db.get(Lesson, published_lesson_id)
    assert revised is not None
    assert revised.content_status == "Draft"
    assert "Revised" in revised.content_body


@pytest.mark.asyncio
async def test_python_seeder_is_idempotent(scratch_session: AsyncSession, tmp_path: Path) -> None:
    from sqlalchemy import func

    db = scratch_session
    root = tmp_path / "content"
    _write_course(root)
    await seed_python(db, str(root))
    await seed_python(db, str(root))

    assert (
        await db.execute(select(func.count(Lesson.id)))
    ).scalar_one() == 2
    assert (
        await db.execute(select(func.count(Problem.id)))
    ).scalar_one() == 1
    assert (
        await db.execute(
            select(func.count(Course.id)).where(Course.slug == "python-engineering")
        )
    ).scalar_one() == 1
