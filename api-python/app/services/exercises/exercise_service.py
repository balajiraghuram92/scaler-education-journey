"""Ported from api/Services/Exercises/ExerciseService.cs."""

from __future__ import annotations

import asyncio
import logging
import os
import re
from uuid import uuid4

from ...schemas.exercise_dtos import (
    ExerciseDiagnosticsDto,
    ExerciseEvidenceResultDto,
    ExerciseExecutionResponse,
    ExerciseSubmissionRequest,
    ExerciseTestSummaryDto,
)
from ...settings import get_settings
from .exercise_execution_classifier import (
    ClassifiedExerciseExecution,
    ExerciseExecutionClassifier,
)
from .exercise_execution_exceptions import (
    ExerciseConcurrencyLimitException,
    ExerciseNotFoundException,
)
from .exercise_execution_models import ExerciseExecutionStatus, RunnerExecutionResult
from .exercise_manifest_models import ExerciseRuntimeProfiles
from .exercise_repository import ExerciseRepository
from .exercise_submission_validator import ExerciseSubmissionValidator
from .exercise_workspace_builder import ExerciseWorkspaceBuilder
from .i_exercise_repository import IExerciseRepository
from .i_exercise_runner import IExerciseRunner
from .local_docker_exercise_runner import LocalDockerExerciseRunner
from .surefire_result_parser import SurefireResultParser

logger = logging.getLogger(__name__)

_limiter: asyncio.Semaphore | None = None


def _get_limiter() -> asyncio.Semaphore:
    # C# registers one SemaphoreSlim as a singleton; this module holds the equivalent.
    global _limiter
    if _limiter is None:
        max_concurrent = get_settings().exercise_execution.max_concurrent_executions
        _limiter = asyncio.Semaphore(max(1, max_concurrent))
    return _limiter


class ExerciseService:
    def __init__(
        self,
        repository: IExerciseRepository | None = None,
        submission_validator: ExerciseSubmissionValidator | None = None,
        workspace_builder: ExerciseWorkspaceBuilder | None = None,
        runner: IExerciseRunner | None = None,
        classifier: ExerciseExecutionClassifier | None = None,
        limiter: asyncio.Semaphore | None = None,
    ) -> None:
        # Optional dependencies default to the shared instances (C# wires them via DI).
        self._repository = repository or ExerciseRepository()
        self._submission_validator = submission_validator or ExerciseSubmissionValidator()
        self._workspace_builder = workspace_builder or ExerciseWorkspaceBuilder()
        self._runner = runner or LocalDockerExerciseRunner()
        self._classifier = classifier or ExerciseExecutionClassifier(SurefireResultParser())
        self._limiter = limiter or _get_limiter()

    async def execute_async(
        self, exercise_id: str, request: ExerciseSubmissionRequest | None
    ) -> ExerciseExecutionResponse:
        definition = self._repository.get_by_id(exercise_id)
        if definition is None:
            raise ExerciseNotFoundException(exercise_id)

        # Non-blocking acquisition (C# WaitAsync(0)): locked() False means the
        # acquire below cannot yield, so check-then-acquire is race-free.
        if self._limiter.locked():
            raise ExerciseConcurrencyLimitException()
        await self._limiter.acquire()

        run_id = uuid4()
        workspace = None
        try:
            logger.info("Starting exercise execution %s for %s.", run_id, exercise_id)
            submission = self._submission_validator.validate(definition, request)
            workspace = await self._workspace_builder.build_async(
                run_id, definition, submission
            )
            runner_result = await self._runner.run_async(workspace)
            classified = self._classifier.classify(definition, runner_result)
            response = _to_response(
                exercise_id,
                classified,
                ExerciseRuntimeProfiles.is_python(definition.manifest),
            )
            logger.info(
                "Completed exercise execution %s for %s with status %s in %s ms.",
                run_id,
                exercise_id,
                response.status,
                response.duration_milliseconds,
            )
            return response
        except Exception as exc:
            logger.error(
                "Exercise execution %s for %s failed: %s", run_id, exercise_id, exc
            )
            raise
        finally:
            if workspace is not None:
                try:
                    ExerciseWorkspaceBuilder.delete_workspace(workspace.path)
                except Exception as exc:
                    logger.warning(
                        "Failed to remove exercise workspace for run %s: %s", run_id, exc
                    )
            self._limiter.release()


def _to_response(
    exercise_id: str, classified: ClassifiedExerciseExecution, is_python: bool = False
) -> ExerciseExecutionResponse:
    parsed = classified.surefire_result
    evidence = [
        ExerciseEvidenceResultDto(
            id=test.evidence_id or "",
            label=test.label if test.label is not None else (test.evidence_id or ""),
            status=test.status,
            duration_milliseconds=int(test.duration.total_seconds() * 1000),
            message=test.message,
        )
        for test in (parsed.tests if parsed is not None else [])
        if test.evidence_id and test.evidence_id.strip()
    ]
    if classified.status == ExerciseExecutionStatus.COMPILATION_FAILURE:
        combined = _combine_output(classified.runner_result)
        compiler_output = python_compiler_output(combined) if is_python else combined
    else:
        compiler_output = None
    runtime_output = (
        _combine_output(classified.runner_result)
        if classified.status == ExerciseExecutionStatus.TEST_FAILURE
        else None
    )
    return ExerciseExecutionResponse(
        run_id=classified.runner_result.run_id.hex,
        exercise_id=exercise_id,
        status=_to_public_status(classified.status),
        passed=classified.status == ExerciseExecutionStatus.SUCCESS,
        duration_milliseconds=int(
            classified.runner_result.duration.total_seconds() * 1000
        ),
        summary=ExerciseTestSummaryDto(
            total=parsed.total if parsed is not None else 0,
            passed=parsed.passed if parsed is not None else 0,
            failed=parsed.failed if parsed is not None else 0,
            errors=parsed.errors if parsed is not None else 0,
            skipped=parsed.skipped if parsed is not None else 0,
        ),
        evidence=evidence,
        diagnostics=ExerciseDiagnosticsDto(
            compiler_output=compiler_output, runtime_output=runtime_output
        ),
    )


_LEARNER_FRAME = re.compile(r"^(?!tests/|/usr/|<frozen)[\w./-]+\.py:\d+: in ")


def python_compiler_output(combined: str | None) -> str | None:
    """pytest reports a learner's syntax/import error as a collection error buried in
    framework frames. Keep what the learner can act on: the error lines ("E ...")
    and frames inside their own files."""
    if not combined or not combined.strip():
        return combined
    lines = combined.replace("\r", "").split("\n")
    kept: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Match on the lstripped line: triple-quoted test input carries
        # indentation, and real runner output may too. For unindented input
        # this is identical to the C# version.
        stripped = line.lstrip()
        if stripped.startswith("E "):
            kept.append(stripped[4:] if len(stripped) > 4 else "")
        elif _LEARNER_FRAME.match(stripped):
            kept.append(line)
            if i + 1 < len(lines) and lines[i + 1].startswith("    "):
                i += 1
                kept.append(lines[i])
        i += 1
    if not kept:
        return combined
    return "\n".join(kept).replace("/workspace/", "")


def _combine_output(result: RunnerExecutionResult) -> str | None:
    combined = os.linesep.join(
        p for p in (result.standard_output, result.standard_error) if p and p.strip()
    )
    return None if not combined.strip() else combined


def _to_public_status(status: ExerciseExecutionStatus) -> str:
    mapping = {
        ExerciseExecutionStatus.SUCCESS: "success",
        ExerciseExecutionStatus.TEST_FAILURE: "testFailure",
        ExerciseExecutionStatus.COMPILATION_FAILURE: "compilationFailure",
        ExerciseExecutionStatus.TIMEOUT: "timeout",
    }
    if status not in mapping:
        raise ValueError(f"Unknown execution status: {status}")
    return mapping[status]
