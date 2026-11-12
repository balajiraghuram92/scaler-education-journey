"""Exercise file reads return on-disk bytes, including CRLF (no database)."""

from __future__ import annotations

from pathlib import Path

from app.services.exercises.exercise_manifest_models import ExerciseDefinition
from app.services.exercises.exercise_metadata_service import ExerciseMetadataService
from app.services.exercises.exercise_solution_service import ExerciseSolutionService

from .exercise_test_factory import create_definition, delete_root, options

CRLF_CONTENT = "package org.example;\r\n\r\n// TODO implement\r\n"


class _StubRepository:
    def __init__(self, definition: ExerciseDefinition) -> None:
        self._definition = definition

    def get_by_id(self, exercise_id: str) -> ExerciseDefinition | None:
        return self._definition


def _write_crlf_files(root: Path) -> None:
    for subdir in ("starter", "solution"):
        for name in ("One.java", "Two.java"):
            target = root / subdir / "src" / "main" / "java" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(CRLF_CONTENT.encode("utf-8"))


def test_metadata_service_returns_starter_content_byte_for_byte(tmp_path: Path) -> None:
    _write_crlf_files(tmp_path)
    definition = create_definition(str(tmp_path))
    service = ExerciseMetadataService(_StubRepository(definition), options())
    try:
        response = service.get_by_id("test-exercise")
        assert [f.starter_content for f in response.files] == [
            CRLF_CONTENT,
            CRLF_CONTENT,
        ]
    finally:
        delete_root(str(tmp_path))


def test_solution_service_returns_solution_content_byte_for_byte(tmp_path: Path) -> None:
    _write_crlf_files(tmp_path)
    definition = create_definition(str(tmp_path))
    service = ExerciseSolutionService(_StubRepository(definition), options())
    try:
        response = service.get_by_id("test-exercise")
        assert [f.content for f in response.files] == [CRLF_CONTENT, CRLF_CONTENT]
    finally:
        delete_root(str(tmp_path))
