"""Translated from LocalDockerExerciseRunnerIntegrationTests.cs.

Needs a Docker daemon, the runner images, and the real exercises tree.
Skipped unless RUN_DOCKER_EXERCISE_TESTS=1 (mirrors the C# Skip + env gate).
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from uuid import uuid4

import docker
import pytest

from app.schemas.exercise_dtos import ExerciseFileSubmission, ExerciseSubmissionRequest
from app.services.exercises.exercise_execution_classifier import (
    ExerciseExecutionClassifier,
)
from app.services.exercises.exercise_execution_models import ExerciseExecutionStatus
from app.services.exercises.exercise_repository import ExerciseRepository
from app.services.exercises.exercise_submission_validator import (
    ExerciseSubmissionValidator,
)
from app.services.exercises.exercise_workspace_builder import ExerciseWorkspaceBuilder
from app.services.exercises.local_docker_exercise_runner import (
    LocalDockerExerciseRunner,
)
from app.services.exercises.surefire_result_parser import SurefireResultParser
from app.settings import ExerciseExecutionSettings
from tests.exercises.exercise_test_factory import delete_root

pytestmark = pytest.mark.docker


def _find_repository_root() -> str:
    current: Path | None = Path(__file__).resolve()
    while current is not None:
        if (current / "exercises").is_dir() and (current / "api" / "StudyTracker.Api.csproj").is_file():
            return str(current)
        current = current.parent if current != current.parent else None
    raise RuntimeError("Could not locate the repository root for Docker exercise integration testing.")


@pytest.mark.asyncio
async def test_golden_solution_executes_through_the_phase1_runner() -> None:
    if os.environ.get("RUN_DOCKER_EXERCISE_TESTS") != "1":
        pytest.skip("Set RUN_DOCKER_EXERCISE_TESTS=1 to run Docker-backed exercise tests.")

    repository_root = _find_repository_root()
    workspace_root = str(
        Path(tempfile.gettempdir()) / "studytracker-docker-tests" / uuid4().hex
    )
    options = ExerciseExecutionSettings(
        exercises_root=os.path.join(repository_root, "exercises"),
        workspace_root=workspace_root,
        runner_image=os.environ.get("EXERCISE_RUNNER_IMAGE", "neuralascent-java-runner:dev"),
        docker_endpoint=os.environ.get("DOCKER_ENDPOINT", "unix:///var/run/docker.sock"),
        maven_cache_volume=os.environ.get("EXERCISE_MAVEN_CACHE_VOLUME", "neuralascent-maven-cache"),
        max_output_bytes=65536,
        max_execution_seconds=120,
    )

    repository = ExerciseRepository(options)
    definition = repository.get_by_id("java-lld-oop3-point-threedpoint")
    assert definition is not None

    request = ExerciseSubmissionRequest(
        files=[
            ExerciseFileSubmission(
                path=f.path,
                content=Path(definition.exercise_root, "solution", f.path).read_text(
                    encoding="utf-8"
                ),
            )
            for f in definition.manifest.files
            if f.editable
        ]
    )
    submission = ExerciseSubmissionValidator(options).validate(definition, request)
    workspace = await ExerciseWorkspaceBuilder(options).build_async(
        uuid4(), definition, submission
    )

    docker_client = docker.DockerClient(base_url=options.docker_endpoint, timeout=30)
    runner = LocalDockerExerciseRunner(docker_client, options)
    try:
        raw_result = await runner.run_async(workspace)
        classified = ExerciseExecutionClassifier(SurefireResultParser()).classify(
            definition, raw_result
        )

        assert classified.status == ExerciseExecutionStatus.SUCCESS
        assert classified.surefire_result is not None
        assert classified.surefire_result.total == 7
        assert classified.surefire_result.passed == 7
    finally:
        ExerciseWorkspaceBuilder.delete_workspace(workspace.path)
        delete_root(workspace_root)
