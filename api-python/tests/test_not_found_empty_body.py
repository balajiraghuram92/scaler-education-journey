"""Unmatched routes answer 404 with an empty body, like ASP.NET (no database)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def _client_with_key(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("API_KEY", "parity-test-key")
    return TestClient(create_app())


def test_unknown_api_path_returns_empty_404(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client_with_key(monkeypatch)
    response = client.get("/api/no-such-thing", headers={"x-api-key": "parity-test-key"})
    assert response.status_code == 404
    assert response.content == b""


def test_typed_id_route_with_wrong_type_returns_empty_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _client_with_key(monkeypatch)
    response = client.get(
        "/api/lessons/not-a-number", headers={"x-api-key": "parity-test-key"}
    )
    assert response.status_code == 404
    assert response.content == b""
