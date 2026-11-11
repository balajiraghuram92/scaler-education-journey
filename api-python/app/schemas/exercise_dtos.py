"""Ported from api/Models/ExerciseDtos.cs."""

from __future__ import annotations

from .base import CamelModel


class ExerciseFileSubmission(CamelModel):
    path: str | None = None
    content: str | None = None


class ExerciseSubmissionRequest(CamelModel):
    files: list[ExerciseFileSubmission] | None = None
    client_request_id: str | None = None


class ExerciseTestSummaryDto(CamelModel):
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0


class ExerciseEvidenceResultDto(CamelModel):
    id: str = ""
    label: str = ""
    status: str = ""
    duration_milliseconds: int = 0
    message: str | None = None


class ExerciseDiagnosticsDto(CamelModel):
    compiler_output: str | None = None
    runtime_output: str | None = None


class ExerciseExecutionResponse(CamelModel):
    run_id: str = ""
    exercise_id: str = ""
    status: str = ""
    passed: bool = False
    duration_milliseconds: int = 0
    summary: ExerciseTestSummaryDto = ExerciseTestSummaryDto()
    evidence: list[ExerciseEvidenceResultDto] = []
    diagnostics: ExerciseDiagnosticsDto = ExerciseDiagnosticsDto()
