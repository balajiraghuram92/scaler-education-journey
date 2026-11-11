"""Ported from api/Data/McqMigrationSeedData.cs.

Reads api/Data/mcq-migration-data.json (or scripts/mcq-migration-data.json) from its
existing location; the file is never copied into api-python/.
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.course_module import CourseModule
from ..models.lesson import Lesson
from ..models.mcq_option import McqOption
from ..models.mcq_question import McqQuestion

_SYNCED_COURSE_SLUGS = {"python-engineering"}

_SLUG_ALIASES = {
    "02-oop-classes-objects": "02-oop-1-intro-lab",
    "03-oop2-encapsulation-inheritance": "03-oop-2-access-modifiers-encapsulation",
}


def _candidate_paths() -> list[str]:
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(here, "..", "..", ".."))
    return [
        os.path.join(repo_root, "scripts", "mcq-migration-data.json"),
        os.path.join(repo_root, "api", "Data", "mcq-migration-data.json"),
        os.path.join(os.getcwd(), "scripts", "mcq-migration-data.json"),
        os.path.join(os.getcwd(), "api", "Data", "mcq-migration-data.json"),
    ]


def _get_case_insensitive(obj: dict, name: str, default=None):  # type: ignore[no-untyped-def]
    for key, value in obj.items():
        if str(key).lower() == name.lower():
            return value
    return default


def _normalize_category(category: str | None) -> str:
    trimmed = (category or "").strip()
    if trimmed in ("Checkpoint", "Additional"):
        return trimmed
    return "Assignment"


def _resolve_data_file() -> str | None:
    return next((p for p in _candidate_paths() if os.path.isfile(p)), None)


def _read_text_file(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


async def seed(session: AsyncSession) -> None:
    resolved = await asyncio.to_thread(_resolve_data_file)
    if resolved is None:
        print("[WARN] mcq-migration-data.json was not found in any candidate path. Skipping MCQ seeding.")
        return

    print(f"[INFO] Loading MCQ migration data from {resolved}")
    try:
        json_content = await asyncio.to_thread(_read_text_file, resolved)
    except OSError as exc:
        print(f"[ERROR] Failed to read MCQ migration file at '{resolved}': {exc}")
        return

    try:
        lesson_groups = json.loads(json_content)
    except ValueError as exc:
        print(f"[ERROR] Failed to parse MCQ migration JSON: {exc}")
        return

    if not lesson_groups:
        print("[WARN] No MCQ migration data found in file.")
        return

    all_lessons = (
        await session.execute(
            select(Lesson).options(
                selectinload(Lesson.module).selectinload(CourseModule.course)
            )
        )
    ).scalars().all()
    lesson_lookup: dict[str, Lesson] = {}
    for lesson in all_lessons:
        if lesson.module is not None and lesson.module.course is not None:
            key = f"{lesson.module.course.slug}/{lesson.module.slug}/{lesson.slug}".lower()
            lesson_lookup[key] = lesson

    existing_rows = (await session.execute(select(McqQuestion.legacy_key))).all()
    existing_keys = {row[0].lower() for row in existing_rows if row[0]}

    added_count = 0
    updated_count = 0
    skipped_count = 0
    total_questions = 0

    for group in lesson_groups:
        course_slug = _get_case_insensitive(group, "courseSlug", "") or ""
        module_slug = _get_case_insensitive(group, "moduleSlug", "") or ""
        lesson_slug = _get_case_insensitive(group, "lessonSlug", "") or ""
        questions = _get_case_insensitive(group, "questions", []) or []
        effective_slug = _SLUG_ALIASES.get(lesson_slug.lower(), lesson_slug)
        lookup_key = f"{course_slug}/{module_slug}/{effective_slug}".lower()
        matched_lesson: Lesson | None = lesson_lookup.get(lookup_key)
        if matched_lesson is None:
            slug_matches = (
                await session.execute(
                    select(Lesson)
                    .options(
                        selectinload(Lesson.module).selectinload(CourseModule.course)
                    )
                    .where(Lesson.slug == effective_slug)
                )
            ).scalars().all()
            matched_lesson = next(
                (
                    candidate
                    for candidate in slug_matches
                    if candidate.module is not None
                    and candidate.module.slug == module_slug
                    and candidate.module.course is not None
                    and candidate.module.course.slug == course_slug
                ),
                None,
            )
            if matched_lesson is not None:
                lesson_lookup[lookup_key] = matched_lesson

        if matched_lesson is None:
            print(
                f"[WARN] Lesson not found for key '{course_slug}/{module_slug}/{effective_slug}'. "
                f"Skipping {len(questions)} question(s)."
            )
            continue

        for q in questions:
            total_questions += 1
            legacy_key = _get_case_insensitive(q, "legacyKey", "") or ""
            if legacy_key.strip() and legacy_key.lower() in existing_keys:
                # Courses whose JSON is canonical get existing rows re-synced, so a
                # corrected answer key or explanation reaches the database.
                if course_slug.lower() in _SYNCED_COURSE_SLUGS and await _sync_existing_question(
                    session, q
                ):
                    updated_count += 1
                skipped_count += 1
                continue

            now = datetime.now(UTC)
            question_entity = McqQuestion(
                lesson_id=matched_lesson.id,
                legacy_key=legacy_key.strip() if legacy_key.strip() else None,
                question_text=_get_case_insensitive(q, "questionText") or "",
                source_type=(
                    _get_case_insensitive(q, "sourceType") or ""
                ).strip() or "FROM_MATERIAL",
                category=_normalize_category(_get_case_insensitive(q, "category")),
                explanation=_get_case_insensitive(q, "explanation") or "",
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            session.add(question_entity)
            await session.flush()
            for opt in _get_case_insensitive(q, "options", []) or []:
                session.add(
                    McqOption(
                        question_id=question_entity.id,
                        option_key=(_get_case_insensitive(opt, "optionKey") or "").strip(),
                        option_text=_get_case_insensitive(opt, "optionText") or "",
                        is_correct=bool(_get_case_insensitive(opt, "isCorrect", False)),
                    )
                )
            if question_entity.legacy_key:
                existing_keys.add(question_entity.legacy_key.lower())
            added_count += 1

            # Batch flush every 250 records to keep change tracking performant
            if added_count % 250 == 0:
                await session.flush()

    if added_count % 250 != 0 or updated_count > 0:
        await session.flush()

    print(
        f"[INFO] MCQ dynamic seeding completed. Added {added_count} questions, "
        f"re-synced {updated_count}, skipped {skipped_count} existing questions "
        f"(total evaluated: {total_questions})."
    )


async def _sync_existing_question(session: AsyncSession, q: dict) -> bool:
    """Update text, explanation, category and option correctness of an existing question.
    Options are matched by key; learner attempts keep their recorded result."""
    key = (_get_case_insensitive(q, "legacyKey", "") or "").strip()
    existing = (
        await session.execute(
            select(McqQuestion)
            .options(selectinload(McqQuestion.options))
            .where(McqQuestion.legacy_key == key)
        )
    ).scalar_one_or_none()
    if existing is None:
        return False

    changed = False

    def _set(current, nxt, apply):  # type: ignore[no-untyped-def]
        nonlocal changed
        if current != nxt:
            apply(nxt)
            changed = True

    _set(
        existing.question_text,
        _get_case_insensitive(q, "questionText") or "",
        lambda v: setattr(existing, "question_text", v),
    )
    _set(
        existing.explanation,
        _get_case_insensitive(q, "explanation") or "",
        lambda v: setattr(existing, "explanation", v),
    )
    _set(
        existing.category,
        _normalize_category(_get_case_insensitive(q, "category")),
        lambda v: setattr(existing, "category", v),
    )
    source_type = _get_case_insensitive(q, "sourceType")
    if source_type and str(source_type).strip():
        _set(
            existing.source_type,
            str(source_type).strip(),
            lambda v: setattr(existing, "source_type", v),
        )

    for opt in _get_case_insensitive(q, "options", []) or []:
        raw_key = _get_case_insensitive(opt, "optionKey")
        if raw_key is None:
            continue  # C# Equals(optionKey, null) never matches
        opt_key = str(raw_key).strip()
        match = next(
            (o for o in existing.options if o.option_key.lower() == opt_key.lower()),
            None,
        )
        if match is None:
            continue
        _set(
            match.option_text,
            _get_case_insensitive(opt, "optionText") or "",
            lambda v, m=match: setattr(m, "option_text", v),
        )
        _set(
            match.is_correct,
            bool(_get_case_insensitive(opt, "isCorrect", False)),
            lambda v, m=match: setattr(m, "is_correct", v),
        )

    if changed:
        existing.updated_at = datetime.now(UTC)
    return changed
