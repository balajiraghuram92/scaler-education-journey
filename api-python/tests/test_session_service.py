"""Session tests translated from tests/StudyTracker.Api.Tests/SessionAndLearnerStateTests.cs.

Only the four session tests live here. The LearnerProgress/MCQ tests in that
file are translated in P3 (tests/test_session_learner_state_progress.py) and
the seeder test in P7, next to the code they exercise.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.models.app_user import AppUser
from app.models.user_session import UserSession
from app.services.auth.jwt_token_service import JwtTokenService
from app.services.auth.session_service import RefreshOutcome, SessionService
from app.settings import AuthSettings

_OPTIONS = AuthSettings(
    Auth__JwtSigningKey="test-signing-key-that-is-at-least-32-bytes-long!!",
    Auth__JwtIssuer="neuralascent",
    Auth__JwtAudience="neuralascent-app",
    Auth__AccessTokenMinutes=30,
    Auth__RememberMeDays=30,
    Auth__SessionHours=24,
    Auth__IdleTimeoutDays=14,
    Auth__RefreshReuseGraceSeconds=60,
)


def _sessions(db: AsyncSession) -> SessionService:
    return SessionService(db, JwtTokenService(_OPTIONS), _OPTIONS)


async def _add_user(db: AsyncSession, status: str = "Approved") -> AppUser:
    user = AppUser(
        email=f"{uuid4().hex}@example.com",
        password_hash="h",
        password_salt="s",
        role="User",
        status=status,
        created_at=datetime.now(UTC),
        totp_enabled=False,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


def _request(refresh_token: str | None = None) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if refresh_token is not None:
        headers.append((b"cookie", f"na_refresh={refresh_token}".encode("ascii")))
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/auth/refresh",
        "headers": headers,
        "client": ("127.0.0.1", 5000),
        "server": ("testserver", 80),
    }
    return Request(scope)


def _response() -> JSONResponse:
    return JSONResponse({})


def _set_cookies(response: JSONResponse) -> dict[str, str]:
    cookies: dict[str, str] = {}
    for header in response.headers.getlist("set-cookie"):
        pair = header.split(";")[0]
        if "=" in pair:
            name, _, value = pair.partition("=")
            cookies[name.strip()] = value.strip().strip('"')
    return cookies


@pytest.mark.asyncio
async def test_start_session_writes_short_lived_access_token_with_session_claim_and_hashed_refresh_token(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    user = await _add_user(db)
    response = _response()

    session = await _sessions(db).start_session(user, True, _request(), response)

    cookies = _set_cookies(response)
    assert "na_auth" in cookies
    assert "na_refresh" in cookies

    claims = jwt.decode(
        cookies["na_auth"],
        "test-signing-key-that-is-at-least-32-bytes-long!!",
        algorithms=["HS256"],
        issuer="neuralascent",
        audience="neuralascent-app",
    )
    assert claims["na_sid"] == str(session.id)
    assert (
        datetime.fromtimestamp(claims["exp"], UTC)
        <= datetime.now(UTC) + timedelta(minutes=31)
    )

    # Only the hash is stored, never the raw token.
    from app.services.auth.session_service import hash_token

    assert hash_token(cookies["na_refresh"]) == session.refresh_token_hash
    assert cookies["na_refresh"] != session.refresh_token_hash
    assert session.expires_at > datetime.now(UTC) + timedelta(days=29)


@pytest.mark.asyncio
async def test_refresh_rotates_token_and_old_token_after_grace_revokes_session(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    user = await _add_user(db)
    sessions = _sessions(db)
    login_response = _response()
    session = await sessions.start_session(user, False, _request(), login_response)
    first_token = _set_cookies(login_response)["na_refresh"]

    refresh_response = _response()
    result = await sessions.refresh(_request(first_token), refresh_response)
    assert result.outcome == RefreshOutcome.REFRESHED
    second_token = _set_cookies(refresh_response)["na_refresh"]
    assert second_token != first_token

    # Re-presenting the rotated-out token inside the grace window is a benign tab race.
    race = await sessions.refresh(_request(first_token), _response())
    assert race.outcome == RefreshOutcome.REFRESHED

    # Outside the grace window it is treated as theft and the whole session is revoked.
    stored = (
        await db.execute(select(UserSession).where(UserSession.id == session.id))
    ).scalar_one()
    stored.rotated_at = datetime.now(UTC) - timedelta(minutes=5)
    await db.flush()

    reuse = await sessions.refresh(_request(first_token), _response())
    assert reuse.outcome == RefreshOutcome.REUSE_DETECTED
    revoked = (
        await db.execute(select(UserSession).where(UserSession.id == session.id))
    ).scalar_one()
    assert revoked.revoked_at is not None

    after_revoke = await sessions.refresh(_request(second_token), _response())
    assert after_revoke.outcome == RefreshOutcome.REVOKED


@pytest.mark.asyncio
async def test_refresh_fails_for_idle_sessions_and_disabled_users(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    sessions = _sessions(db)

    idle_user = await _add_user(db)
    idle_response = _response()
    idle = await sessions.start_session(idle_user, True, _request(), idle_response)
    idle_row = (
        await db.execute(select(UserSession).where(UserSession.id == idle.id))
    ).scalar_one()
    idle_row.last_seen_at = datetime.now(UTC) - timedelta(days=20)
    await db.flush()
    idle_token = _set_cookies(idle_response)["na_refresh"]
    idle_result = await sessions.refresh(_request(idle_token), _response())
    assert idle_result.outcome == RefreshOutcome.EXPIRED

    disabled_user = await _add_user(db)
    disabled_response = _response()
    await sessions.start_session(disabled_user, True, _request(), disabled_response)
    disabled_user.status = "Disabled"
    await db.flush()
    disabled_token = _set_cookies(disabled_response)["na_refresh"]
    disabled_result = await sessions.refresh(_request(disabled_token), _response())
    assert disabled_result.outcome == RefreshOutcome.USER_INACTIVE

    missing = await sessions.refresh(_request(None), _response())
    assert missing.outcome == RefreshOutcome.MISSING
    invalid = await sessions.refresh(_request("not-a-real-token"), _response())
    assert invalid.outcome == RefreshOutcome.INVALID


@pytest.mark.asyncio
async def test_revoke_all_ends_every_session_and_active_check_reflects_it(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    user = await _add_user(db)
    sessions = _sessions(db)
    a = await sessions.start_session(user, True, _request(), _response())
    b = await sessions.start_session(user, False, _request(), _response())

    active = await sessions.list_active(user.id, a.id)
    assert len(active) == 2
    assert next(s for s in active if s.id == a.id).is_current is True

    assert await sessions.revoke_all(user.id, None, "LogoutAll") == 2
    assert await sessions.is_session_active(a.id, user.id) is False
    assert await sessions.is_session_active(b.id, user.id) is False
    assert await sessions.list_active(user.id, None) == []

    # A session cannot be revoked through another account.
    other = await _add_user(db)
    c = await sessions.start_session(other, True, _request(), _response())
    assert await sessions.revoke(c.id, user.id, "x") is False
    assert await sessions.is_session_active(c.id, other.id) is True
