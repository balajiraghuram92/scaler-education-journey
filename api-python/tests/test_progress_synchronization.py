"""Translated from tests/StudyTracker.Api.Tests/ProgressSynchronizationTests.cs."""

from __future__ import annotations

from uuid import uuid4

from app.models.study_task_content_link import StudyTaskContentLink
from app.services.progress_service import ProgressResult


def test_progress_result_constructs_with_valid_sync_data() -> None:
    correlation_id = uuid4()
    result = ProgressResult(
        success=True,
        entity_type="Lesson",
        entity_id=42,
        is_completed=True,
        synchronized_task_ids=[101, 102],
        correlation_id=correlation_id,
    )

    assert result.success is True
    assert result.entity_type == "Lesson"
    assert result.entity_id == 42
    assert result.is_completed is True
    assert len(result.synchronized_task_ids) == 2
    assert result.correlation_id == correlation_id


def test_verified_mapping_filter_only_selects_verified_status() -> None:
    links = [
        StudyTaskContentLink(task_id=1, lesson_id=10, mapping_status="Verified"),
        StudyTaskContentLink(task_id=2, lesson_id=10, mapping_status="Proposed"),
        StudyTaskContentLink(task_id=3, lesson_id=10, mapping_status="Rejected"),
        StudyTaskContentLink(task_id=4, lesson_id=10, mapping_status="Conflict"),
    ]

    verified = [link for link in links if link.mapping_status == "Verified"]

    assert len(verified) == 1
    assert verified[0].task_id == 1


def test_error_result_is_sanitized_without_leaking_raw_exception() -> None:
    result = ProgressResult(
        success=False,
        entity_type="StudyTask",
        entity_id=99,
        correlation_id=uuid4(),
        error="An error occurred while updating task progress. Please refer to traceId for support.",
    )

    assert result.success is False
    assert result.error is not None
    assert "SELECT" not in result.error
    assert "Npgsql" not in result.error
    assert "Host=" not in result.error
    assert "traceId" in result.error
