"""Ported from api/Services/Exercises/IExerciseRunner.cs."""

from __future__ import annotations

from typing import Protocol

from .exercise_execution_models import PreparedExerciseWorkspace, RunnerExecutionResult


class IExerciseRunner(Protocol):
    async def run_async(self, workspace: PreparedExerciseWorkspace) -> RunnerExecutionResult:
        ...
