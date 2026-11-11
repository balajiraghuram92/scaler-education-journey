"""Ported from api/Services/Exercises/ExerciseExecutionModels.cs."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from uuid import UUID

from .exercise_manifest_models import ExerciseDefinition


class ExerciseExecutionStatus(str, Enum):
    SUCCESS = "Success"
    TEST_FAILURE = "TestFailure"
    COMPILATION_FAILURE = "CompilationFailure"
    TIMEOUT = "Timeout"


@dataclass
class PreparedExerciseWorkspace:
    run_id: UUID
    path: str
    definition: ExerciseDefinition


@dataclass
class RunnerExecutionResult:
    run_id: UUID
    exit_code: int = 0
    timed_out: bool = False
    standard_output: str = ""
    standard_error: str = ""
    surefire_xml: str | None = None
    duration: timedelta = field(default_factory=timedelta)


@dataclass
class ParsedSurefireTest:
    test_method: str
    status: str
    evidence_id: str | None = None
    label: str | None = None
    duration: timedelta = field(default_factory=timedelta)
    message: str | None = None


@dataclass
class ParsedSurefireResult:
    total: int = 0
    passed: int = 0
    failed: int = 0
    errors: int = 0
    skipped: int = 0
    tests: list[ParsedSurefireTest] = field(default_factory=list)
