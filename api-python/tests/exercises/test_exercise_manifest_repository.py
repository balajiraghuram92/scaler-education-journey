"""Translated from ExerciseManifestRepositoryTests.cs."""

from __future__ import annotations

import json
from pathlib import Path

from app.services.exercises.exercise_repository import ExerciseRepository
from app.settings import ExerciseExecutionSettings

from .exercise_test_factory import create_definition, create_exercise_root, delete_root


def _manifest_json(root: str) -> str:
    manifest = create_definition(root).manifest
    return json.dumps(
        {
            "id": manifest.id,
            "runtime": {
                "profile": manifest.runtime.profile,
                "javaVersion": manifest.runtime.java_version,
                "timeoutSeconds": manifest.runtime.timeout_seconds,
            },
            "files": [
                {
                    "id": f.id,
                    "path": f.path,
                    "displayName": f.display_name,
                    "editable": f.editable,
                }
                for f in manifest.files
            ],
            "testSuite": {
                "visible": manifest.test_suite.visible,
                "path": manifest.test_suite.path,
                "className": manifest.test_suite.class_name,
            },
            "evidence": [
                {"id": e.id, "label": e.label, "testMethod": e.test_method}
                for e in manifest.evidence
            ],
        }
    )


def test_repository_loads_manifest_by_id_without_exercise_specific_knowledge() -> None:
    root = create_exercise_root()
    try:
        (Path(root) / "exercise.json").write_text(_manifest_json(root), encoding="utf-8")
        repository = ExerciseRepository(ExerciseExecutionSettings(exercises_root=root))

        definition = repository.get_by_id("test-exercise")

        assert definition is not None
        assert definition.manifest.runtime.profile == "java-maven"
        assert len(definition.editable_files) == 2
        assert repository.get_by_id("unknown") is None
    finally:
        delete_root(root)
