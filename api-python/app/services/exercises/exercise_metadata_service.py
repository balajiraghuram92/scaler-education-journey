"""Ported from api/Services/Exercises/ExerciseMetadataService.cs."""

from __future__ import annotations

import os

from ...schemas.exercise_metadata_dtos import (
    ExerciseEvidenceMetadataDto,
    ExerciseFileMetadataDto,
    ExerciseMetadataResponse,
)
from ...settings import ExerciseExecutionSettings, get_settings
from .exercise_execution_exceptions import (
    ExerciseInfrastructureException,
    ExerciseNotFoundException,
)
from .exercise_manifest_models import (
    ExerciseDefinition,
    ExerciseFileManifest,
    ExerciseRuntimeProfiles,
    is_link,
    resolve_inside,
)
from .i_exercise_repository import IExerciseRepository


class ExerciseMetadataService:
    def __init__(
        self,
        repository: IExerciseRepository,
        options: ExerciseExecutionSettings | None = None,
    ) -> None:
        self._repository = repository
        self._options = options or get_settings().exercise_execution

    def get_by_id(self, exercise_id: str) -> ExerciseMetadataResponse:
        definition = self._repository.get_by_id(exercise_id)
        if definition is None:
            raise ExerciseNotFoundException(exercise_id)

        # Python exercises also show provided (read-only) modules the learner builds on.
        include_provided = ExerciseRuntimeProfiles.is_python(definition.manifest)
        files = sorted(
            (f for f in definition.manifest.files if f.editable or include_provided),
            key=lambda f: 0 if f.editable else 1,
        )
        return ExerciseMetadataResponse(
            id=definition.manifest.id,
            lesson_slug=definition.manifest.lesson_slug,
            title=definition.manifest.title,
            language=definition.manifest.language,
            difficulty=definition.manifest.difficulty,
            estimated_minutes=definition.manifest.estimated_minutes,
            instructions=definition.manifest.instructions,
            files=[
                ExerciseFileMetadataDto(
                    id=f.id,
                    path=f.path,
                    display_name=f.display_name,
                    editable=f.editable,
                    starter_content=self._read_starter_content(definition, f),
                )
                for f in files
            ],
            evidence=[
                ExerciseEvidenceMetadataDto(id=e.id, label=e.label)
                for e in definition.manifest.evidence
            ],
        )

    def _read_starter_content(
        self, definition: ExerciseDefinition, file: ExerciseFileManifest
    ) -> str:
        try:
            starter_root = resolve_inside(definition.exercise_root, "starter")
            starter_path = resolve_inside(starter_root, file.path)
            if not os.path.isfile(starter_path) or is_link(starter_path):
                raise ExerciseInfrastructureException("Trusted starter source is unavailable.")
            # newline="" keeps CRLF byte-for-byte; utf-8-sig strips a BOM like File.ReadAllText.
            with open(starter_path, encoding="utf-8-sig", newline="") as fh:
                content = fh.read()
            if len(content.encode("utf-8")) > self._options.max_file_bytes:
                raise ExerciseInfrastructureException(
                    "Trusted starter source exceeds the configured file limit."
                )
            return content
        except ExerciseInfrastructureException:
            raise
        except (OSError, ValueError) as exc:
            raise ExerciseInfrastructureException(
                "Trusted starter source is unavailable.", exc
            ) from exc
