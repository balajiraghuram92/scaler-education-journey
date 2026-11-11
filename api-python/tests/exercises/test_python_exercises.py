"""Translated from PythonExerciseTests.cs."""

from __future__ import annotations

import json
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.app_user import AppUser
from app.models.course import Course
from app.models.course_module import CourseModule
from app.models.lesson import Lesson
from app.models.problem import Problem
from app.schemas.exercise_dtos import (
    ExerciseDiagnosticsDto,
    ExerciseEvidenceResultDto,
    ExerciseExecutionResponse,
    ExerciseFileSubmission,
    ExerciseSubmissionRequest,
    ExerciseTestSummaryDto,
)
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
from app.services.exercises.exercise_manifest_models import (
    ExerciseDefinition,
    ExerciseEvidenceManifest,
    ExerciseFileManifest,
    ExerciseManifest,
    ExerciseRuntimeManifest,
    ExerciseTestSuiteManifest,
)
from app.services.exercises.exercise_progress_service import (
    ExerciseDraftFileDto,
    ExerciseProgressService,
)
from app.services.exercises.exercise_repository import ExerciseRepository
from app.services.exercises.exercise_service import python_compiler_output
from app.services.exercises.exercise_workspace_builder import ExerciseWorkspaceBuilder
from app.services.exercises.surefire_result_parser import SurefireResultParser
from app.services.learner_progress_service import LearnerProgressService
from app.settings import ExerciseExecutionSettings

from .exercise_test_factory import delete_root, options


def _python_definition(root: str) -> ExerciseDefinition:
    manifest = ExerciseManifest(
        id="py-test-exercise",
        language="python",
        runtime=ExerciseRuntimeManifest(profile="python-pytest", timeout_seconds=20),
        files=[
            ExerciseFileManifest(
                id="impl", path="pkg/impl.py", display_name="impl.py", editable=True
            ),
            ExerciseFileManifest(
                id="models", path="pkg/models.py", display_name="models.py", editable=False
            ),
        ],
        test_suite=ExerciseTestSuiteManifest(path="tests"),
        evidence=[
            ExerciseEvidenceManifest(
                id="adds", label="Adds numbers", test_method="test_adds"
            ),
            ExerciseEvidenceManifest(
                id="rejects", label="Rejects bad input", test_method="test_rejects"
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


def _python_root() -> str:
    root = Path(tempfile.gettempdir()) / "studytracker-py-exercise-tests" / uuid4().hex
    (root / "starter" / "pkg").mkdir(parents=True)
    (root / "solution" / "pkg").mkdir(parents=True)
    (root / "tests" / "helpers").mkdir(parents=True)
    (root / "starter" / "pkg" / "impl.py").write_text(
        "def add(a, b):\n    raise NotImplementedError\n", encoding="utf-8"
    )
    (root / "starter" / "pkg" / "models.py").write_text("LIMIT = 10\n", encoding="utf-8")
    (root / "solution" / "pkg" / "impl.py").write_text(
        "def add(a, b):\n    return a + b\n", encoding="utf-8"
    )
    (root / "tests" / "test_impl.py").write_text(
        "def test_adds():\n    pass\n", encoding="utf-8"
    )
    (root / "tests" / "conftest.py").write_text("", encoding="utf-8")
    (root / "tests" / "helpers" / "data.py").write_text("X = 1\n", encoding="utf-8")
    return str(root)


def _run(xml: str | None, exit_code: int, stdout: str = "") -> RunnerExecutionResult:
    return RunnerExecutionResult(
        run_id=uuid4(), exit_code=exit_code, standard_output=stdout, surefire_xml=xml
    )


@pytest.mark.asyncio
async def test_workspace_builder_copies_provided_files_submission_and_whole_test_directory() -> None:
    root = _python_root()
    workspace_root = str(
        Path(tempfile.gettempdir()) / "studytracker-py-ws" / uuid4().hex
    )
    try:
        builder = ExerciseWorkspaceBuilder(options(workspace_root))
        submission = {
            "pkg/impl.py": ExerciseFileSubmission(
                path="pkg/impl.py", content="def add(a, b):\n    return a + b\n"
            )
        }

        workspace = await builder.build_async(
            uuid4(), _python_definition(root), submission
        )

        assert (
            Path(workspace.path, "pkg", "models.py").read_text(encoding="utf-8")  # noqa: ASYNC240
            == "LIMIT = 10\n"
        )
        assert (
            "return a + b"
            in Path(workspace.path, "pkg", "impl.py").read_text(encoding="utf-8")  # noqa: ASYNC240
        )
        assert Path(workspace.path, "tests", "test_impl.py").is_file()  # noqa: ASYNC240
        assert Path(workspace.path, "tests", "conftest.py").is_file()  # noqa: ASYNC240
        assert Path(workspace.path, "tests", "helpers", "data.py").is_file()  # noqa: ASYNC240
        assert not Path(workspace.path, "pom.xml").exists()  # noqa: ASYNC240
    finally:
        delete_root(root)
        delete_root(workspace_root)


def test_repository_loads_python_manifest_with_test_directory() -> None:
    root = _python_root()
    try:
        manifest = _python_definition(root).manifest
        (Path(root) / "exercise.json").write_text(
            json.dumps(
                {
                    "id": manifest.id,
                    "language": manifest.language,
                    "runtime": {"profile": "python-pytest", "timeoutSeconds": 20},
                    "files": [
                        {
                            "id": f.id,
                            "path": f.path,
                            "displayName": f.display_name,
                            "editable": f.editable,
                        }
                        for f in manifest.files
                    ],
                    "testSuite": {"path": "tests"},
                    "evidence": [
                        {"id": e.id, "label": e.label, "testMethod": e.test_method}
                        for e in manifest.evidence
                    ],
                }
            ),
            encoding="utf-8",
        )
        repository = ExerciseRepository(ExerciseExecutionSettings(exercises_root=root))

        definition = repository.get_by_id("py-test-exercise")

        assert definition is not None
        assert len(definition.editable_files) == 1
    finally:
        delete_root(root)


def test_repository_rejects_python_manifest_without_tests() -> None:
    root = _python_root()
    try:
        shutil.rmtree(Path(root) / "tests")
        manifest = _python_definition(root).manifest
        (Path(root) / "exercise.json").write_text(
            json.dumps({"id": manifest.id, "runtime": {"profile": "python-pytest"}}),
            encoding="utf-8",
        )
        with pytest.raises(ValueError):
            ExerciseRepository(ExerciseExecutionSettings(exercises_root=root))
    finally:
        delete_root(root)


def test_classifier_treats_collection_errors_as_compilation_failure() -> None:
    classifier = ExerciseExecutionClassifier(SurefireResultParser())
    xml = """
        <testsuites><testsuite name="pytest" errors="1" failures="0" tests="1">
          <testcase classname="" name="tests.test_impl" time="0.0"><error message="collection failure">SyntaxError: invalid syntax</error></testcase>
        </testsuite></testsuites>
        """

    result = classifier.classify(
        _python_definition("root"),
        _run(xml, 2, "ERROR collecting tests/test_impl.py\nE   SyntaxError: invalid syntax"),
    )

    assert result.status == ExerciseExecutionStatus.COMPILATION_FAILURE


def test_classifier_python_failures_are_test_failures_and_parametrized_cases_map_to_evidence() -> None:
    classifier = ExerciseExecutionClassifier(SurefireResultParser())
    xml = """
        <testsuites><testsuite name="pytest" errors="0" failures="1" tests="3">
          <testcase classname="tests.test_impl" name="test_adds" time="0.01" />
          <testcase classname="tests.test_impl" name="test_rejects[negative]" time="0.01"><failure message="AssertionError: expected ValueError">trace</failure></testcase>
          <testcase classname="tests.test_impl" name="test_rejects[zero]" time="0.01" />
        </testsuite></testsuites>
        """

    result = classifier.classify(_python_definition("root"), _run(xml, 1))

    assert result.status == ExerciseExecutionStatus.TEST_FAILURE
    assert result.surefire_result is not None
    failed = next(t for t in result.surefire_result.tests if t.status == "failed")
    assert failed.evidence_id == "rejects[negative]"
    assert failed.label == "Rejects bad input [negative]"
    assert failed.message is not None and "expected ValueError" in failed.message


def test_classifier_all_passing_is_success_and_missing_report_with_syntax_error_is_compilation_failure() -> None:
    classifier = ExerciseExecutionClassifier(SurefireResultParser())
    xml = """
        <testsuites><testsuite tests="2"><testcase name="test_adds" /><testcase name="test_rejects" /></testsuite></testsuites>
        """

    assert (
        classifier.classify(_python_definition("root"), _run(xml, 0)).status
        == ExerciseExecutionStatus.SUCCESS
    )
    assert (
        classifier.classify(
            _python_definition("root"),
            _run(None, 2, '  File "pkg/impl.py", line 3\nIndentationError: unexpected indent'),
        ).status
        == ExerciseExecutionStatus.COMPILATION_FAILURE
    )
    with pytest.raises(ExerciseInfrastructureException):
        classifier.classify(_python_definition("root"), _run(None, 1, "something odd"))


def test_python_compiler_output_keeps_learner_error_lines_and_drops_framework_frames() -> None:
    raw = """
        ==================================== ERRORS ====================================
        __________________ ERROR collecting tests/test_count_freq.py ___________________
        /usr/local/lib/python3.13/site-packages/_pytest/python.py:498: in importtestmodule
            mod = import_path(
        <frozen importlib._bootstrap>:1404: in _gcd_import
            ???
        tests/test_count_freq.py:3: in <module>
            from config.countFreq import count_frequency
        config/helpers.py:2: in <module>
            import missing_module
        E     File "/workspace/config/countFreq.py", line 1
        E       def count_frequency(arr)
        E                               ^
        E   SyntaxError: expected ':'
        =========================== short test summary info ============================
        """

    cleaned = python_compiler_output(raw)
    assert cleaned is not None

    assert "SyntaxError: expected ':'" in cleaned
    assert 'File "config/countFreq.py", line 1' in cleaned
    assert "config/helpers.py:2: in <module>" in cleaned
    assert "import missing_module" in cleaned
    assert "site-packages" not in cleaned
    assert "<frozen" not in cleaned
    assert "tests/test_count_freq.py" not in cleaned  # hidden tests stay hidden
    assert "/workspace/" not in cleaned
    assert python_compiler_output("unparsed output") == "unparsed output"


@pytest.mark.asyncio
async def test_progress_service_records_runs_restores_draft_and_auto_solves_on_success(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    now = datetime.now(UTC)
    user = AppUser(
        email=f"{uuid4().hex}@example.com",
        password_hash="h",
        password_salt="s",
        role="User",
        status="Approved",
        created_at=now,
        totp_enabled=False,
    )
    db.add(user)
    await db.flush()
    course = Course(
        slug="python-engineering",
        title="P",
        description="d",
        order_index=0,
        path_type="Course",
        is_published=True,
        created_at=now,
        updated_at=now,
    )
    db.add(course)
    await db.flush()
    module = CourseModule(
        course_id=course.id,
        slug="m",
        title="M",
        description="d",
        badge="M",
        order_index=0,
        created_at=now,
        updated_at=now,
    )
    db.add(module)
    await db.flush()
    lesson = Lesson(
        module_id=module.id,
        slug="py-01",
        title="L",
        description="",
        lecture_number=1,
        class_date="2026-01-01",
        content_body="",
        horstmann_ref="",
        estimated_minutes=45,
        is_completed=False,
        order_index=0,
        created_at=now,
        updated_at=now,
        difficulty="Intermediate",
        content_status="Published",
    )
    db.add(lesson)
    await db.flush()
    problem = Problem(
        lesson_id=lesson.id,
        slug="py-test-exercise",
        title="P",
        difficulty="Warm-up",
        package_name="",
        test_class_name="",
        problem_statement="",
        requirements_body="",
        worked_example="",
        hints="",
        language="python",
        run_command="",
        reference_solution="",
        source_type="FROM_MATERIAL",
        is_completed=False,
        order_index=0,
        created_at=now,
        updated_at=now,
    )
    db.add(problem)
    await db.flush()
    await db.refresh(user)
    await db.refresh(problem)

    learner = LearnerProgressService(db)
    service = ExerciseProgressService(db, learner)
    request = ExerciseSubmissionRequest(
        files=[
            ExerciseFileSubmission(
                path="pkg/impl.py", content="def add(a, b): return a - b"
            )
        ]
    )

    def response(passed: bool, ok: int) -> ExerciseExecutionResponse:
        return ExerciseExecutionResponse(
            run_id="run",
            exercise_id="py-test-exercise",
            status="success" if passed else "testFailure",
            passed=passed,
            duration_milliseconds=120,
            summary=ExerciseTestSummaryDto(total=2, passed=ok, failed=2 - ok, errors=0, skipped=0),
            evidence=[
                ExerciseEvidenceResultDto(
                    id="adds",
                    label="Adds numbers",
                    status="passed" if ok >= 1 else "failed",
                    duration_milliseconds=5,
                    message=None,
                ),
                ExerciseEvidenceResultDto(
                    id="rejects",
                    label="Rejects bad input",
                    status="passed" if ok >= 2 else "failed",
                    duration_milliseconds=5,
                    message="boom" if ok < 2 else None,
                ),
            ],
            diagnostics=ExerciseDiagnosticsDto(compiler_output=None, runtime_output=None),
        )

    await service.record_run(user.id, "py-test-exercise", request, response(False, 1))
    after_fail = await service.get_state(user.id, "py-test-exercise")
    assert after_fail.attempt_count == 1
    assert after_fail.solved is False
    assert len(after_fail.draft_files) == 1
    assert after_fail.draft_files[0].content == "def add(a, b): return a - b"
    assert problem.id not in await learner.get_solved_problem_ids(user.id)

    await service.save_draft(
        user.id,
        "py-test-exercise",
        [ExerciseDraftFileDto(path="pkg/impl.py", content="def add(a, b): return a + b")],
    )
    state = await service.get_state(user.id, "py-test-exercise")
    assert len(state.draft_files) == 1
    assert state.draft_files[0].content is not None and "a + b" in state.draft_files[0].content

    await service.record_run(user.id, "py-test-exercise", request, response(True, 2))
    after_pass = await service.get_state(user.id, "py-test-exercise")
    assert after_pass.solved is True
    assert after_pass.attempt_count == 2
    assert after_pass.best_attempt is not None
    assert after_pass.best_attempt.status == "success"
    assert problem.id in await learner.get_solved_problem_ids(user.id)
    assert any(
        e.event_type == "ExerciseRun"
        for e in await learner.get_activity(user.id, 20, None)
    )
