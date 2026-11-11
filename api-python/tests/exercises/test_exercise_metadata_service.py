"""Translated from ExerciseMetadataServiceTests.cs."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.exercises.exercise_execution_exceptions import (
    ExerciseNotFoundException,
)
from app.services.exercises.exercise_manifest_models import ExerciseDefinition
from app.services.exercises.exercise_metadata_service import ExerciseMetadataService

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


def test_returns_learner_safe_metadata_and_trusted_starter_content() -> None:
    root = create_exercise_root()
    try:
        starter_dir = Path(root) / "starter" / "src" / "main" / "java"
        starter_dir.mkdir(parents=True)
        (starter_dir / "One.java").write_text("class One { }", encoding="utf-8")
        (starter_dir / "Two.java").write_text("class Two { }", encoding="utf-8")

        definition = create_definition(root)
        definition.manifest.instructions = "Implement the protected coordinates."
        service = ExerciseMetadataService(_StubRepository(definition), options())

        metadata = service.get_by_id("test-exercise")

        assert metadata.id == "test-exercise"
        assert len(metadata.files) == 2
        assert (
            next(f for f in metadata.files if f.id == "one").starter_content
            == "class One { }"
        )
        assert (
            next(e for e in metadata.evidence if e.id == "one-evidence").label
            == "One works"
        )
        assert all("TrustedTest" not in f.path for f in metadata.files)
        assert metadata.instructions == "Implement the protected coordinates."
    finally:
        delete_root(root)


def test_missing_exercise_throws_not_found_exception() -> None:
    root = create_exercise_root()
    try:
        definition = create_definition(root)
        service = ExerciseMetadataService(_StubRepository(definition), options())

        with pytest.raises(ExerciseNotFoundException):
            service.get_by_id("missing")
    finally:
        delete_root(root)
