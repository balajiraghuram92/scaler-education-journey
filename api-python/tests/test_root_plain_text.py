"""GET / answers plain text like the C# minimal API (no database)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


def test_root_returns_plain_text_without_quotes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_KEY", "parity-test-key")
    client = TestClient(create_app())
    response = client.get("/", headers={"x-api-key": "parity-test-key"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert '"' not in response.text
    assert response.text == "StudyTracker API is running. Use /health for service health."
