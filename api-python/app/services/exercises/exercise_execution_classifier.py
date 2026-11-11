"""Ported from api/Services/Exercises/ExerciseExecutionClassifier.cs."""

from __future__ import annotations

from dataclasses import dataclass

from .exercise_execution_exceptions import ExerciseInfrastructureException
from .exercise_execution_models import (
    ExerciseExecutionStatus,
    ParsedSurefireResult,
    RunnerExecutionResult,
)
from .exercise_manifest_models import ExerciseDefinition, ExerciseRuntimeProfiles
from .surefire_result_parser import SurefireResultParser

_COMPILATION_MARKERS = (
    "COMPILATION ERROR",
    "Compilation failure",
    "maven-compiler-plugin",
    "cannot find symbol",
    "';' expected",
    "illegal start of",
)

# Python has no compile step: the equivalent is pytest failing to import the learner's
# modules while collecting tests (SyntaxError, IndentationError, ImportError, NameError at import).
_PYTHON_COLLECTION_MARKERS = (
    "ERROR collecting",
    "SyntaxError",
    "IndentationError",
    "TabError",
    "ImportError",
    "ModuleNotFoundError",
)


@dataclass
class ClassifiedExerciseExecution:
    status: ExerciseExecutionStatus
    runner_result: RunnerExecutionResult
    surefire_result: ParsedSurefireResult | None = None


class ExerciseExecutionClassifier:
    def __init__(self, surefire_result_parser: SurefireResultParser | None = None) -> None:
        self._parser = surefire_result_parser or SurefireResultParser()

    def classify(
        self, definition: ExerciseDefinition, runner_result: RunnerExecutionResult
    ) -> ClassifiedExerciseExecution:
        if runner_result.timed_out:
            return ClassifiedExerciseExecution(
                status=ExerciseExecutionStatus.TIMEOUT, runner_result=runner_result
            )
        if ExerciseRuntimeProfiles.is_python(definition.manifest):
            return self._classify_python(definition, runner_result)
        if runner_result.surefire_xml and runner_result.surefire_xml.strip():
            parsed = self._parser.parse(runner_result.surefire_xml, definition)
            if parsed.failed > 0 or parsed.errors > 0:
                return ClassifiedExerciseExecution(
                    status=ExerciseExecutionStatus.TEST_FAILURE,
                    runner_result=runner_result,
                    surefire_result=parsed,
                )
            if runner_result.exit_code == 0 and parsed.total > 0:
                return ClassifiedExerciseExecution(
                    status=ExerciseExecutionStatus.SUCCESS,
                    runner_result=runner_result,
                    surefire_result=parsed,
                )
            raise ExerciseInfrastructureException(
                "Maven exited unsuccessfully despite a non-failing Surefire report."
            )
        if _looks_like_compilation_failure(
            runner_result.standard_output, runner_result.standard_error
        ):
            return ClassifiedExerciseExecution(
                status=ExerciseExecutionStatus.COMPILATION_FAILURE,
                runner_result=runner_result,
            )
        raise ExerciseInfrastructureException(
            "The exercise runner exited without producing authoritative Surefire results."
        )

    def _classify_python(
        self, definition: ExerciseDefinition, runner_result: RunnerExecutionResult
    ) -> ClassifiedExerciseExecution:
        parsed: ParsedSurefireResult | None = None
        if runner_result.surefire_xml and runner_result.surefire_xml.strip():
            try:
                parsed = self._parser.parse(runner_result.surefire_xml, definition)
            except ExerciseInfrastructureException:
                parsed = None  # an empty report (nothing collected) is handled below

        output = f"{runner_result.standard_output}\n{runner_result.standard_error}"
        parsed_collection_error = (
            parsed is not None
            and any(
                test.status == "error"
                and (
                    not test.test_method.startswith("test")
                    or "collection failure" in (test.message or "").lower()
                )
                for test in parsed.tests
            )
        )
        collection_failed = (
            parsed_collection_error
            or "ERROR collecting" in output
            or "Interrupted: " in output
        )
        if collection_failed or (
            parsed is None
            and any(marker in output for marker in _PYTHON_COLLECTION_MARKERS)
        ):
            return ClassifiedExerciseExecution(
                status=ExerciseExecutionStatus.COMPILATION_FAILURE,
                runner_result=runner_result,
            )
        if parsed is None:
            raise ExerciseInfrastructureException(
                "The Python runner exited without producing a pytest report."
            )
        if parsed.failed > 0 or parsed.errors > 0:
            return ClassifiedExerciseExecution(
                status=ExerciseExecutionStatus.TEST_FAILURE,
                runner_result=runner_result,
                surefire_result=parsed,
            )
        if runner_result.exit_code == 0 and parsed.total > 0:
            return ClassifiedExerciseExecution(
                status=ExerciseExecutionStatus.SUCCESS,
                runner_result=runner_result,
                surefire_result=parsed,
            )
        raise ExerciseInfrastructureException(
            "pytest exited unsuccessfully despite a non-failing report."
        )


def _looks_like_compilation_failure(standard_output: str, standard_error: str) -> bool:
    output = f"{standard_output}\n{standard_error}".lower()
    return any(marker.lower() in output for marker in _COMPILATION_MARKERS)
