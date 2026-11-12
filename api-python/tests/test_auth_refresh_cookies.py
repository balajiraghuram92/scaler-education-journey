"""Failed refresh clears both cookies on the sent response (no database)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.services.auth.session_service import SessionService


def test_refresh_with_unknown_token_deletes_both_cookies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _no_session(self: object, token_hash: str) -> None:
        return None

    monkeypatch.setattr(SessionService, "_find_by_refresh_hash", _no_session)
    monkeypatch.setattr(SessionService, "_find_by_previous_refresh_hash", _no_session)
    monkeypatch.setenv("API_KEY", "parity-test-key")
    client = TestClient(create_app())

    response = client.post(
        "/api/auth/refresh",
        headers={"x-api-key": "parity-test-key"},
        cookies={"na_refresh": "unknown-refresh-token"},
    )

    assert response.status_code == 401
    deletions = response.headers.get_list("set-cookie")
    assert len(deletions) == 2
    assert any(c.startswith("na_auth=") for c in deletions)
    assert any(c.startswith("na_refresh=") for c in deletions)
    assert all("Max-Age=0" in c for c in deletions)
