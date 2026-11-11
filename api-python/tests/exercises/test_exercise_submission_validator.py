"""Translated from ExerciseSubmissionValidatorTests.cs."""

from __future__ import annotations

import pytest

from app.schemas.exercise_dtos import ExerciseFileSubmission, ExerciseSubmissionRequest
from app.services.exercises.exercise_execution_exceptions import (
    ExerciseSubmissionValidationException,
)
from app.services.exercises.exercise_submission_validator import (
    ExerciseSubmissionValidator,
)

from .exercise_test_factory import create_definition, options, valid_submission


def test_validator_accepts_exactly_the_editable_manifest_files() -> None:
    definition = create_definition("C:\\exercise")
    validator = ExerciseSubmissionValidator(options())

    submitted = validator.validate(definition, valid_submission())

    assert len(submitted) == 2


@pytest.mark.parametrize(
    "path",
    [
        "pom.xml",
        "tests/src/test/java/TrustedTest.java",
        "../pom.xml",
        "src/main/java/Unknown.java",
    ],
)
def test_validator_rejects_trusted_or_unsafe_paths(path: str) -> None:
    definition = create_definition("C:\\exercise")
    validator = ExerciseSubmissionValidator(options())
    request = ExerciseSubmissionRequest(
        files=[
            ExerciseFileSubmission(path=path, content="not allowed"),
            ExerciseFileSubmission(path="src/main/java/Two.java", content="class Two {}"),
        ]
    )

    with pytest.raises(ExerciseSubmissionValidationException):
        validator.validate(definition, request)


def test_validator_rejects_missing_editable_file() -> None:
    definition = create_definition("C:\\exercise")
    validator = ExerciseSubmissionValidator(options())
    request = ExerciseSubmissionRequest(
        files=[ExerciseFileSubmission(path="src/main/java/One.java", content="class One {}")]
    )

    with pytest.raises(ExerciseSubmissionValidationException) as exc_info:
        validator.validate(definition, request)

    assert any("Two.java" in error for error in exc_info.value.errors)
