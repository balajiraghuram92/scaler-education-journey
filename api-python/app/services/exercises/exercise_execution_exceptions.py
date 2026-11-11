"""Ported from api/Services/Exercises/ExerciseExecutionExceptions.cs."""

from __future__ import annotations


class ExerciseSubmissionValidationException(Exception):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("The exercise submission is invalid.")
        self.errors = errors


class ExerciseInfrastructureException(Exception):
    pass


class ExerciseRunnerUnavailableException(Exception):
    pass


class ExerciseNotFoundException(Exception):
    def __init__(self, exercise_id: str) -> None:
        super().__init__(f"Exercise '{exercise_id}' was not found.")
        self.exercise_id = exercise_id


class ExerciseSolutionNotFoundException(Exception):
    def __init__(self, exercise_id: str) -> None:
        super().__init__(f"Exercise '{exercise_id}' does not have a reference solution.")
        self.exercise_id = exercise_id


class ExerciseConcurrencyLimitException(Exception):
    def __init__(self) -> None:
        super().__init__("The exercise execution concurrency limit has been reached.")
