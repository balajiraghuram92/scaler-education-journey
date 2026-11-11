"""Test helpers. Ported from tests/StudyTracker.Api.Tests/Exercises/ExerciseTestFactory.cs."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

from app.schemas.exercise_dtos import ExerciseFileSubmission, ExerciseSubmissionRequest
from app.services.exercises.exercise_manifest_models import (
    ExerciseDefinition,
    ExerciseEvidenceManifest,
    ExerciseFileManifest,
    ExerciseManifest,
    ExerciseRuntimeManifest,
    ExerciseTestSuiteManifest,
)
from app.settings import ExerciseExecutionSettings


def create_definition(root: str) -> ExerciseDefinition:
    manifest = ExerciseManifest(
        id="test-exercise",
        runtime=ExerciseRuntimeManifest(profile="java-maven", timeout_seconds=10),
        files=[
            ExerciseFileManifest(
                id="one",
                path="src/main/java/One.java",
                display_name="One.java",
                editable=True,
            ),
            ExerciseFileManifest(
                id="two",
                path="src/main/java/Two.java",
                display_name="Two.java",
                editable=True,
            ),
            ExerciseFileManifest(
                id="read-only",
                path="src/main/java/ReadOnly.java",
                display_name="ReadOnly.java",
                editable=False,
            ),
        ],
        test_suite=ExerciseTestSuiteManifest(
            path="tests/src/test/java/TrustedTest.java", class_name="TrustedTest"
        ),
        evidence=[
            ExerciseEvidenceManifest(
                id="one-evidence", label="One works", test_method="testOne"
            ),
            ExerciseEvidenceManifest(
                id="two-evidence", label="Two works", test_method="testTwo"
            ),
        ],
    )
    return ExerciseDefinition(
        manifest=manifest,
        manifest_path=str(Path(root) / "exercise.json"),
        exercise_root=root,
        editable_files={f.path: f for f in manifest.files if f.editable},
        evidence_by_test_method={e.test_method: e for e in manifest.evidence},
    )


def create_exercise_root() -> str:
    root = Path(tempfile.gettempdir()) / "studytracker-exercise-tests" / uuid4().hex
    (root / "tests" / "src" / "test" / "java").mkdir(parents=True)
    (root / "pom.xml").write_text("<project />", encoding="utf-8")
    (root / "tests" / "src" / "test" / "java" / "TrustedTest.java").write_text(
        "class TrustedTest {}", encoding="utf-8"
    )
    return str(root)


def delete_root(root: str | None) -> None:
    if root and root.strip():
        shutil.rmtree(root, ignore_errors=True)


def options(workspace_root: str | None = None) -> ExerciseExecutionSettings:
    return ExerciseExecutionSettings(
        workspace_root=workspace_root
        or str(
            Path(tempfile.gettempdir())
            / "studytracker-exercise-workspaces"
            / uuid4().hex
        ),
        max_file_bytes=1024,
        max_submission_bytes=2048,
        max_output_bytes=4096,
        max_execution_seconds=10,
    )


def valid_submission() -> ExerciseSubmissionRequest:
    return ExerciseSubmissionRequest(
        files=[
            ExerciseFileSubmission(path="src/main/java/One.java", content="class One {}"),
            ExerciseFileSubmission(path="src/main/java/Two.java", content="class Two {}"),
        ]
    )
