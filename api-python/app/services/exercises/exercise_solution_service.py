"""Ported from api/Services/Exercises/ExerciseSolutionService.cs."""

from __future__ import annotations

import os

from ...schemas.exercise_metadata_dtos import (
    ExerciseSolutionFileDto,
    ExerciseSolutionResponse,
)
from ...settings import ExerciseExecutionSettings, get_settings
from .exercise_execution_exceptions import (
    ExerciseInfrastructureException,
    ExerciseNotFoundException,
    ExerciseSolutionNotFoundException,
)
from .exercise_manifest_models import (
    ExerciseDefinition,
    ExerciseFileManifest,
    is_link,
    resolve_inside,
)
from .i_exercise_repository import IExerciseRepository


class ExerciseSolutionService:
    def __init__(
        self,
        repository: IExerciseRepository,
        options: ExerciseExecutionSettings | None = None,
    ) -> None:
        self._repository = repository
        self._options = options or get_settings().exercise_execution

    def get_by_id(self, exercise_id: str) -> ExerciseSolutionResponse:
        definition = self._repository.get_by_id(exercise_id)
        if definition is None:
            raise ExerciseNotFoundException(exercise_id)
        files = [
            ExerciseSolutionFileDto(
                id=f.id,
                path=f.path,
                display_name=f.display_name,
                language=definition.manifest.language,
                content=self._read_solution_content(definition, f),
                display_order=index,
            )
            for index, f in enumerate(
                [f for f in definition.manifest.files if f.editable]
            )
        ]
        if not files:
            raise ExerciseSolutionNotFoundException(exercise_id)
        return ExerciseSolutionResponse(exercise_id=definition.manifest.id, files=files)

    def _read_solution_content(
        self, definition: ExerciseDefinition, file: ExerciseFileManifest
    ) -> str:
        try:
            solution_root = resolve_inside(definition.exercise_root, "solution")
            solution_path = resolve_inside(solution_root, file.path)
            if (
                not os.path.isdir(solution_root)
                or not os.path.isfile(solution_path)
                or _contains_link(solution_root, file.path)
            ):
                raise ExerciseSolutionNotFoundException(definition.manifest.id)
            # newline="" keeps CRLF byte-for-byte; utf-8-sig strips a BOM like File.ReadAllText.
            with open(solution_path, encoding="utf-8-sig", newline="") as fh:
                content = fh.read()
            if len(content.encode("utf-8")) > self._options.max_file_bytes:
                raise ExerciseInfrastructureException(
                    "Trusted reference solution exceeds the configured file limit."
                )
            return content
        except ExerciseSolutionNotFoundException:
            raise
        except ExerciseInfrastructureException:
            raise
        except (OSError, ValueError) as exc:
            raise ExerciseInfrastructureException(
                "Trusted reference solution is unavailable.", exc
            ) from exc


def _contains_link(root: str, relative_path: str) -> bool:
    if is_link(root):
        return True
    current = root
    for segment in relative_path.split("/"):
        current = os.path.join(current, segment)
        if is_link(current):
            return True
    return False
