"""Translated from ExerciseWorkspaceBuilderTests.cs."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from uuid import uuid4

import pytest

from app.services.exercises.exercise_submission_validator import (
    ExerciseSubmissionValidator,
)
from app.services.exercises.exercise_workspace_builder import ExerciseWorkspaceBuilder

from .exercise_test_factory import (
    create_definition,
    create_exercise_root,
    delete_root,
    options,
    valid_submission,
)


@pytest.mark.asyncio
async def test_builder_copies_trusted_pom_and_tests_and_only_submitted_source() -> None:
    exercise_root = create_exercise_root()
    workspace_root = str(
        Path(tempfile.gettempdir()) / "studytracker-workspace-tests" / uuid4().hex
    )
    try:
        definition = create_definition(exercise_root)
        opts = options(workspace_root)
        submission = ExerciseSubmissionValidator(opts).validate(
            definition, valid_submission()
        )

        workspace = await ExerciseWorkspaceBuilder(opts).build_async(
            uuid4(), definition, submission
        )

        assert os.path.isfile(os.path.join(workspace.path, "pom.xml"))  # noqa: ASYNC240
        assert os.path.isfile(  # noqa: ASYNC240
            os.path.join(workspace.path, "src", "test", "java", "TrustedTest.java")
        )
        with open(  # noqa: ASYNC230
            os.path.join(workspace.path, "src", "main", "java", "One.java"),
            encoding="utf-8",
        ) as fh:
            assert fh.read() == "class One {}"
        assert not os.path.exists(os.path.join(workspace.path, "exercise.json"))  # noqa: ASYNC240
        assert not os.path.exists(  # noqa: ASYNC240
            os.path.join(workspace.path, "solution", "src", "main", "java", "One.java")
        )

        ExerciseWorkspaceBuilder.delete_workspace(workspace.path)
        assert not os.path.isdir(workspace.path)  # noqa: ASYNC240
    finally:
        delete_root(exercise_root)
        delete_root(workspace_root)
