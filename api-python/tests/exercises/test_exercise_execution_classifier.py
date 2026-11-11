"""Translated from ExerciseExecutionClassifierTests.cs."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.services.exercises.exercise_execution_classifier import (
    ExerciseExecutionClassifier,
)
from app.services.exercises.exercise_execution_exceptions import (
    ExerciseInfrastructureException,
)
from app.services.exercises.exercise_execution_models import (
    ExerciseExecutionStatus,
    RunnerExecutionResult,
)
from app.services.exercises.surefire_result_parser import SurefireResultParser

from .exercise_test_factory import create_definition


def test_classifier_returns_test_failure_when_surefire_reports_failure() -> None:
    classifier = ExerciseExecutionClassifier(SurefireResultParser())
    result = classifier.classify(
        create_definition("C:\\exercise"),
        RunnerExecutionResult(
            run_id=uuid4(),
            exit_code=1,
            surefire_xml='<testsuite><testcase name="testOne"><failure message="bad" /></testcase></testsuite>',
        ),
    )

    assert result.status == ExerciseExecutionStatus.TEST_FAILURE


def test_classifier_returns_compilation_failure_from_compiler_diagnostics_without_surefire() -> None:
    classifier = ExerciseExecutionClassifier(SurefireResultParser())
    result = classifier.classify(
        create_definition("C:\\exercise"),
        RunnerExecutionResult(
            run_id=uuid4(), exit_code=1, standard_error="[ERROR] COMPILATION ERROR"
        ),
    )

    assert result.status == ExerciseExecutionStatus.COMPILATION_FAILURE


def test_classifier_returns_timeout_before_looking_for_reports() -> None:
    classifier = ExerciseExecutionClassifier(SurefireResultParser())
    result = classifier.classify(
        create_definition("C:\\exercise"),
        RunnerExecutionResult(run_id=uuid4(), exit_code=137, timed_out=True),
    )

    assert result.status == ExerciseExecutionStatus.TIMEOUT


def test_classifier_throws_infrastructure_failure_when_no_authoritative_result_exists() -> None:
    classifier = ExerciseExecutionClassifier(SurefireResultParser())

    with pytest.raises(ExerciseInfrastructureException):
        classifier.classify(
            create_definition("C:\\exercise"),
            RunnerExecutionResult(
                run_id=uuid4(), exit_code=1, standard_error="network unavailable"
            ),
        )
