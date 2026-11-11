"""Translated from tests/StudyTracker.Api.Tests/LifecycleAndProblemDetailsTests.cs."""

from __future__ import annotations

import json

import pytest

from app.cli import build_parser
from app.errors import problem_body


def test_problem_details_should_conform_to_rfc7807_without_secrets() -> None:
    correlation_id = "corr-test-12345"
    body = problem_body(
        status=500,
        title="An internal error occurred processing your request.",
        detail="Internal server error. Please refer to traceId for support.",
        instance="/api/verticals",
        trace_id=correlation_id,
        type_url="https://tools.ietf.org/html/rfc7231#section-6.6.1",
    )

    payload = json.dumps(body)

    assert '"status": 500' in payload
    assert '"traceId": "corr-test-12345"' in payload
    assert "password" not in payload.lower()
    assert "secret" not in payload.lower()
    assert "host=" not in payload.lower()


@pytest.mark.parametrize(
    ("flag", "expected_migrate", "expected_seed"),
    [
        ("--migrate", True, False),
        ("--seed-reference-data", False, True),
        ("--seed", False, True),
    ],
)
def test_cli_flag_detection_should_identify_dedicated_execution_modes(
    flag: str, expected_migrate: bool, expected_seed: bool
) -> None:
    args = build_parser().parse_args([flag])

    assert args.migrate is expected_migrate
    assert args.seed_reference_data is expected_seed
