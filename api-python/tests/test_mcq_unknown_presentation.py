"""Unknown-presentation errors carry the bare message, no extra quotes (no database)."""

from __future__ import annotations

from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

PID = "00000000-0000-0000-0000-000000000000"
EXPECTED = f"Presentation '{PID}' not found."


class _MissingPresentationService:
    def __init__(self, session: object) -> None:
        pass

    async def record_attempt(
        self, presentation_id: UUID, selected_option_key: str, user_id: int | None
    ) -> object:
        raise KeyError(f"Presentation '{presentation_id}' not found.")

    async def retry(self, presentation_id: UUID, user_id: int | None) -> object:
        raise KeyError(f"Presentation '{presentation_id}' not found.")


def _client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(
        "app.routers.v2_endpoints.McqService", _MissingPresentationService
    )
    monkeypatch.setenv("API_KEY", "parity-test-key")
    return TestClient(create_app())


def test_attempt_unknown_presentation_error_has_no_extra_quotes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client(monkeypatch)
    response = client.post(
        f"/api/v2/practice-questions/{PID}/attempts",
        headers={"x-api-key": "parity-test-key"},
        json={"selectedOptionKey": "A"},
    )
    assert response.status_code == 404
    assert response.json() == {"error": EXPECTED}


def test_retry_unknown_presentation_error_has_no_extra_quotes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client(monkeypatch)
    response = client.post(
        f"/api/v2/practice-questions/{PID}/retry",
        headers={"x-api-key": "parity-test-key"},
    )
    assert response.status_code == 404
    assert response.json() == {"error": EXPECTED}
