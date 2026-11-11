"""Ported from api/Services/Exercises/ExerciseWorkspaceBuilder.cs."""

from __future__ import annotations

import asyncio
import os
import shutil
import tempfile
from uuid import UUID

from ...schemas.exercise_dtos import ExerciseFileSubmission
from ...settings import ExerciseExecutionSettings, get_settings
from .exercise_execution_exceptions import ExerciseInfrastructureException
from .exercise_execution_models import PreparedExerciseWorkspace
from .exercise_manifest_models import (
    ExerciseDefinition,
    ExerciseManifest,
    ExerciseRuntimeProfiles,
    is_link,
    resolve_inside,
)


class ExerciseWorkspaceBuilder:
    def __init__(self, options: ExerciseExecutionSettings | None = None) -> None:
        self._options = options or get_settings().exercise_execution

    async def build_async(
        self,
        run_id: UUID,
        definition: ExerciseDefinition,
        submission: dict[str, ExerciseFileSubmission],
    ) -> PreparedExerciseWorkspace:
        workspace_root = (
            self._options.workspace_root
            if self._options.workspace_root and self._options.workspace_root.strip()
            else os.path.join(tempfile.gettempdir(), "studytracker-exercises")
        )
        os.makedirs(workspace_root, exist_ok=True)
        workspace_path = resolve_inside(workspace_root, run_id.hex)
        os.makedirs(workspace_path, exist_ok=True)
        try:
            if ExerciseRuntimeProfiles.is_python(definition.manifest):
                await _build_python_workspace_async(workspace_path, definition, submission)
                return PreparedExerciseWorkspace(
                    run_id=run_id, path=workspace_path, definition=definition
                )
            pom_source = os.path.join(definition.exercise_root, "pom.xml")
            pom_destination = resolve_inside(workspace_path, "pom.xml")
            shutil.copyfile(pom_source, pom_destination)

            test_source = resolve_inside(
                definition.exercise_root, definition.manifest.test_suite.path
            )
            test_destination = resolve_inside(
                workspace_path, _resolve_test_workspace_path(definition.manifest)
            )
            os.makedirs(os.path.dirname(test_destination), exist_ok=True)
            shutil.copyfile(test_source, test_destination)

            for file in submission.values():
                destination = resolve_inside(workspace_path, file.path or "")
                os.makedirs(os.path.dirname(destination), exist_ok=True)
                await _write_text_async(destination, file.content or "")
            return PreparedExerciseWorkspace(
                run_id=run_id, path=workspace_path, definition=definition
            )
        except Exception:
            ExerciseWorkspaceBuilder.delete_workspace(workspace_path)
            raise

    @staticmethod
    def delete_workspace(workspace_path: str | None) -> None:
        if not workspace_path or not workspace_path.strip():
            return
        if not os.path.isdir(workspace_path):
            return
        shutil.rmtree(workspace_path, ignore_errors=False)


async def _build_python_workspace_async(
    workspace_path: str,
    definition: ExerciseDefinition,
    submission: dict[str, ExerciseFileSubmission],
) -> None:
    """Python layout: provided (non-editable) starter files, the learner's editable
    files, and the trusted pytest directory copied to `tests/`."""
    starter_root = resolve_inside(definition.exercise_root, "starter")
    for provided in definition.manifest.files:
        if provided.editable:
            continue
        source = resolve_inside(starter_root, provided.path)
        _copy_trusted_file(source, resolve_inside(workspace_path, provided.path))

    for file in submission.values():
        destination = resolve_inside(workspace_path, file.path or "")
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        await _write_text_async(destination, file.content or "")

    tests_source = resolve_inside(
        definition.exercise_root, definition.manifest.test_suite.path
    )
    tests_destination = resolve_inside(workspace_path, "tests")
    for dirpath, _dirnames, filenames in os.walk(tests_source):
        for name in filenames:
            test_file = os.path.join(dirpath, name)
            relative = await _relative_posix_async(test_file, tests_source)
            if "__pycache__" in relative:
                continue
            _copy_trusted_file(
                test_file, resolve_inside(tests_destination, relative)
            )


def _copy_trusted_file(source: str, destination: str) -> None:
    if not os.path.isfile(source) or is_link(source):
        raise ExerciseInfrastructureException("A trusted exercise file is missing or linked.")
    parent = os.path.dirname(destination)
    if parent:
        os.makedirs(parent, exist_ok=True)
    shutil.copyfile(source, destination)


async def _write_text_async(destination: str, content: str) -> None:
    await asyncio.to_thread(_write_text, destination, content)


def _write_text(destination: str, content: str) -> None:
    # Written without a BOM, like the C# UTF8Encoding(false).
    with open(destination, "w", encoding="utf-8", newline="") as fh:
        fh.write(content)


async def _relative_posix_async(test_file: str, tests_source: str) -> str:
    return await asyncio.to_thread(_relative_posix, test_file, tests_source)


def _relative_posix(test_file: str, tests_source: str) -> str:
    # os.path.relpath touches the filesystem (abspath → getcwd), so like the
    # writes above it runs in a thread rather than on the event loop.
    return os.path.relpath(test_file, tests_source).replace(os.sep, "/")


def _resolve_test_workspace_path(manifest: ExerciseManifest) -> str:
    if manifest.runtime.profile.lower() == "java-maven":
        prefix = "tests/"
        if manifest.test_suite.path.startswith(prefix):
            return manifest.test_suite.path[len(prefix):]
        return manifest.test_suite.path
    raise ExerciseInfrastructureException(
        f"No workspace layout is registered for runtime profile '{manifest.runtime.profile}'."
    )
