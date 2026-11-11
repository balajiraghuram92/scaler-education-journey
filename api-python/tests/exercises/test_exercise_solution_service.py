"""Translated from ExerciseSolutionServiceTests.cs."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.exercises.exercise_execution_exceptions import (
    ExerciseInfrastructureException,
    ExerciseNotFoundException,
    ExerciseSolutionNotFoundException,
)
from app.services.exercises.exercise_manifest_models import ExerciseDefinition
from app.services.exercises.exercise_solution_service import ExerciseSolutionService

from .exercise_test_factory import (
    create_definition,
    create_exercise_root,
    delete_root,
    options,
)


class _StubRepository:
    def __init__(self, definition: ExerciseDefinition) -> None:
        self._definition = definition

    def get_by_id(self, exercise_id: str) -> ExerciseDefinition | None:
        return self._definition if exercise_id == self._definition.manifest.id else None


def test_returns_all_manifest_editable_solution_files_in_display_order() -> None:
    root = create_exercise_root()
    try:
        solution_dir = Path(root) / "solution" / "src" / "main" / "java"
        solution_dir.mkdir(parents=True)
        (solution_dir / "One.java").write_text(
            "class One { int value = 1; }", encoding="utf-8"
        )
        (solution_dir / "Two.java").write_text(
            "class Two { int value = 2; }", encoding="utf-8"
        )

        definition = create_definition(root)
        definition.manifest.language = "java"
        service = ExerciseSolutionService(_StubRepository(definition), options())

        solution = service.get_by_id("test-exercise")

        assert solution.exercise_id == "test-exercise"
        assert len(solution.files) == 2
        assert [f.id for f in solution.files] == ["one", "two"]
        assert solution.files[0].content == "class One { int value = 1; }"
        assert all(f.language == "java" for f in solution.files)
        assert solution.files[0].display_order == 0
        assert solution.files[1].display_order == 1
    finally:
        delete_root(root)


def test_missing_reference_solution_is_reported_without_breaking_metadata_lookup() -> None:
    root = create_exercise_root()
    try:
        definition = create_definition(root)
        service = ExerciseSolutionService(_StubRepository(definition), options())

        with pytest.raises(ExerciseSolutionNotFoundException):
            service.get_by_id("test-exercise")
    finally:
        delete_root(root)


def test_unknown_exercise_id_does_not_resolve_a_file_path() -> None:
    root = create_exercise_root()
    try:
        definition = create_definition(root)
        service = ExerciseSolutionService(_StubRepository(definition), options())

        with pytest.raises(ExerciseNotFoundException):
            service.get_by_id("unknown")
    finally:
        delete_root(root)


def test_unsafe_manifest_solution_path_is_rejected_before_filesystem_access() -> None:
    root = create_exercise_root()
    try:
        definition = create_definition(root)
        definition.manifest.files[0].path = "../outside.java"
        service = ExerciseSolutionService(_StubRepository(definition), options())

        with pytest.raises(ExerciseInfrastructureException):
            service.get_by_id("test-exercise")
    finally:
        delete_root(root)
