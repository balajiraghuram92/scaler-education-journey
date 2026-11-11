"""Translated from ExerciseServiceTests.cs."""

from __future__ import annotations

import asyncio
import os
import tempfile
from datetime import timedelta
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from app.services.exercises.exercise_execution_classifier import (
    ExerciseExecutionClassifier,
)
from app.services.exercises.exercise_execution_models import (
    PreparedExerciseWorkspace,
    RunnerExecutionResult,
)
from app.services.exercises.exercise_manifest_models import ExerciseDefinition
from app.services.exercises.exercise_service import ExerciseService
from app.services.exercises.exercise_submission_validator import (
    ExerciseSubmissionValidator,
)
from app.services.exercises.exercise_workspace_builder import ExerciseWorkspaceBuilder
from app.services.exercises.surefire_result_parser import SurefireResultParser

from .exercise_test_factory import (
    create_definition,
    create_exercise_root,
    delete_root,
    options,
    valid_submission,
)


class _StubRepository:
    def __init__(self, definition: ExerciseDefinition) -> None:
        self._definition = definition

    def get_by_id(self, exercise_id: str) -> ExerciseDefinition | None:
        return self._definition if exercise_id == self._definition.manifest.id else None


class _StubRunner:
    def __init__(self, result: RunnerExecutionResult) -> None:
        self._result = result

    async def run_async(self, workspace: PreparedExerciseWorkspace) -> RunnerExecutionResult:
        return RunnerExecutionResult(
            run_id=workspace.run_id,
            exit_code=self._result.exit_code,
            timed_out=self._result.timed_out,
            standard_output=self._result.standard_output,
            standard_error=self._result.standard_error,
            surefire_xml=self._result.surefire_xml,
            duration=self._result.duration,
        )


@pytest.mark.asyncio
async def test_service_returns_normalized_success_and_cleans_workspace() -> None:
    exercise_root = create_exercise_root()
    workspace_root = str(
        Path(tempfile.gettempdir()) / "studytracker-service-tests" / uuid4().hex
    )
    try:
        definition = create_definition(exercise_root)
        opts = options(workspace_root)
        service = ExerciseService(
            _StubRepository(definition),
            ExerciseSubmissionValidator(opts),
            ExerciseWorkspaceBuilder(opts),
            _StubRunner(
                RunnerExecutionResult(
                    run_id=UUID(int=0),
                    exit_code=0,
                    surefire_xml='<testsuite><testcase name="testOne" /><testcase name="testTwo" /></testsuite>',
                    duration=timedelta(milliseconds=25),
                )
            ),
            ExerciseExecutionClassifier(SurefireResultParser()),
            asyncio.Semaphore(1),
        )

        response = await service.execute_async("test-exercise", valid_submission())

        assert response.status == "success"
        assert response.passed is True
        assert response.summary.passed == 2
        assert response.run_id != ""
        # Tests use synchronous file I/O with noqa (single-threaded loop, so
        # blocking harms nothing); shipped code goes through asyncio.to_thread.
        remaining = os.listdir(workspace_root) if os.path.isdir(workspace_root) else []  # noqa: ASYNC240
        assert remaining == []
    finally:
        delete_root(exercise_root)
        delete_root(workspace_root)
