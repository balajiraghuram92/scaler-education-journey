"""Ported from api/Services/Exercises/ExerciseSubmissionValidator.cs."""

from __future__ import annotations

from ...schemas.exercise_dtos import ExerciseFileSubmission, ExerciseSubmissionRequest
from ...settings import ExerciseExecutionSettings, get_settings
from .exercise_execution_exceptions import ExerciseSubmissionValidationException
from .exercise_manifest_models import ExerciseDefinition, is_safe_relative_path


class ExerciseSubmissionValidator:
    def __init__(self, options: ExerciseExecutionSettings | None = None) -> None:
        self._options = options or get_settings().exercise_execution

    def validate(
        self,
        definition: ExerciseDefinition,
        request: ExerciseSubmissionRequest | None,
    ) -> dict[str, ExerciseFileSubmission]:
        errors: list[str] = []
        submitted: dict[str, ExerciseFileSubmission] = {}
        if request is None or request.files is None or len(request.files) == 0:
            errors.append("At least one editable file must be submitted.")
            raise ExerciseSubmissionValidationException(errors)

        total_bytes = 0
        for file in request.files:
            if file is None or not file.path or not file.path.strip():
                errors.append("Every submitted file must have a path.")
                continue
            if not is_safe_relative_path(file.path):
                errors.append(f"Submitted path '{file.path}' is not a safe relative path.")
                continue
            if file.path not in definition.editable_files:
                errors.append(
                    f"Submitted path '{file.path}' is not declared editable by the exercise manifest."
                )
                continue
            if file.content is None:
                errors.append(f"Submitted file '{file.path}' must contain text content.")
                continue
            if file.path in submitted:
                errors.append(f"Submitted path '{file.path}' was provided more than once.")
                continue
            submitted[file.path] = file
            file_bytes = len(file.content.encode("utf-8"))
            if file_bytes > self._options.max_file_bytes:
                errors.append(
                    f"Submitted file '{file.path}' exceeds the per-file size limit."
                )
            total_bytes += file_bytes

        for editable_path in definition.editable_files:
            if editable_path not in submitted:
                errors.append(f"Editable file '{editable_path}' is missing from the submission.")

        if total_bytes > self._options.max_submission_bytes:
            errors.append("The submission exceeds the total size limit.")

        if errors:
            raise ExerciseSubmissionValidationException(errors)
        return submitted
