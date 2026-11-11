"""Ported from api/Services/Exercises/ExerciseRepository.cs."""

from __future__ import annotations

import json
import logging
import os

from ...settings import ExerciseExecutionSettings, get_settings
from .exercise_manifest_models import (
    ExerciseDefinition,
    ExerciseManifest,
    ExerciseRuntimeProfiles,
    is_link,
    is_safe_relative_path,
    parse_manifest,
    resolve_inside,
)

logger = logging.getLogger(__name__)


class ExerciseRepository:
    def __init__(self, options: ExerciseExecutionSettings | None = None) -> None:
        opts = options or get_settings().exercise_execution
        root = _resolve_exercise_root(opts.exercises_root)
        self._definitions = _load_definitions(root)
        if not self._definitions:
            raise ValueError(f"No exercise manifests were found under '{root}'.")

    def get_by_id(self, exercise_id: str) -> ExerciseDefinition | None:
        return self._definitions.get(exercise_id)


_repository: ExerciseRepository | None = None


def get_exercise_repository() -> ExerciseRepository:
    """Shared repository (C# registers it as a singleton). Also used by the V2 chapter reader."""
    global _repository
    if _repository is None:
        _repository = ExerciseRepository()
    return _repository


def _resolve_exercise_root(configured_root: str) -> str:
    root = (
        configured_root
        if configured_root and configured_root.strip()
        else os.path.join(os.getcwd(), "exercises")
    )
    full_root = os.path.abspath(root)
    if not os.path.isdir(full_root):
        raise ValueError(f"Configured exercise root does not exist: '{full_root}'.")
    return full_root


def _load_definitions(root: str) -> dict[str, ExerciseDefinition]:
    definitions: dict[str, ExerciseDefinition] = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        if "exercise.json" not in filenames:
            continue
        manifest_path = os.path.join(dirpath, "exercise.json")
        if is_link(manifest_path):
            raise ValueError(f"Exercise manifest links are not allowed: '{manifest_path}'.")
        with open(manifest_path, encoding="utf-8") as fh:
            manifest = parse_manifest(json.load(fh))
        if not manifest.id:
            raise ValueError(f"Exercise manifest is empty: '{manifest_path}'.")
        _validate_manifest(manifest, manifest_path)
        if manifest.id in definitions:
            raise ValueError(f"Duplicate exercise ID '{manifest.id}'.")
        exercise_root = os.path.dirname(manifest_path)
        definitions[manifest.id] = ExerciseDefinition(
            manifest=manifest,
            manifest_path=manifest_path,
            exercise_root=exercise_root,
            editable_files={
                f.path: f for f in manifest.files if f.editable
            },
            evidence_by_test_method={e.test_method: e for e in manifest.evidence},
        )
        logger.info("Loaded exercise manifest %s from %s.", manifest.id, manifest_path)
    return definitions


def _validate_manifest(manifest: ExerciseManifest, manifest_path: str) -> None:
    if not manifest.id.strip() or not manifest.runtime.profile.strip():
        raise ValueError(
            f"Exercise manifest '{manifest_path}' must define an ID and runtime profile."
        )
    exercise_root = os.path.dirname(manifest_path)
    editable_ids: set[str] = set()
    file_paths: set[str] = set()
    for f in manifest.files:
        if (
            not f.id.strip()
            or f.id in editable_ids
            or f.path in file_paths
            or not is_safe_relative_path(f.path)
        ):
            raise ValueError(
                f"Exercise manifest '{manifest_path}' contains invalid or duplicate file metadata."
            )
        editable_ids.add(f.id)
        file_paths.add(f.path)
    if sum(1 for f in manifest.files if f.editable) == 0:
        raise ValueError(
            f"Exercise manifest '{manifest_path}' declares no editable files."
        )
    if not is_safe_relative_path(manifest.test_suite.path):
        raise ValueError(
            f"Exercise manifest '{manifest_path}' contains an unsafe test path."
        )
    test_path = resolve_inside(exercise_root, manifest.test_suite.path)
    if ExerciseRuntimeProfiles.is_python(manifest):
        # Python suites are a directory of trusted pytest files (test_*.py, conftest.py, helpers).
        has_tests = False
        if os.path.isdir(test_path) and not is_link(test_path):
            for _dirpath, _dirnames, filenames in os.walk(test_path):
                if any(name.startswith("test_") and name.endswith(".py") for name in filenames):
                    has_tests = True
                    break
        if not has_tests:
            raise ValueError(
                f"Trusted pytest directory is missing, linked or empty: '{test_path}'."
            )
        for f in manifest.files:
            starter_path = resolve_inside(
                os.path.join(exercise_root, "starter"), f.path
            )
            if not os.path.isfile(starter_path) or is_link(starter_path):
                raise ValueError(
                    f"Python exercise '{manifest.id}' is missing starter file '{f.path}'."
                )
    elif not os.path.isfile(test_path) or is_link(test_path):
        raise ValueError(f"Trusted test file is missing or linked: '{test_path}'.")
    if manifest.runtime.profile.lower() == "java-maven":
        pom_path = os.path.join(exercise_root, "pom.xml")
        if not os.path.isfile(pom_path) or is_link(pom_path):
            raise ValueError(
                f"Java Maven exercise is missing a trusted pom.xml: '{pom_path}'."
            )
    evidence_ids: set[str] = set()
    test_methods: set[str] = set()
    for evidence in manifest.evidence:
        if (
            not evidence.id.strip()
            or not evidence.test_method.strip()
            or evidence.id in evidence_ids
            or evidence.test_method in test_methods
        ):
            raise ValueError(
                f"Exercise manifest '{manifest_path}' contains invalid evidence mappings."
            )
        evidence_ids.add(evidence.id)
        test_methods.add(evidence.test_method)
