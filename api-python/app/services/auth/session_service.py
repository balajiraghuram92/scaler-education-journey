"""Ported from api/Services/Auth/SessionService.cs.

Owns the session lifecycle: issue on login, rotate on refresh (with reuse
detection), revoke on logout, and answer "is this session still valid" for
every authenticated request.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
import time
from datetime import datetime, timedelta, timezone
from enum import Enum
from uuid import UUID

from fastapi import Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...models.app_user import AppUser
from ...models.user_session import UserSession
from ...schemas.base import CamelModel, DotNetDateTime
from ...settings import AuthSettings, get_settings
from .jwt_token_service import JwtTokenService


class RefreshOutcome(str, Enum):
    REFRESHED = "Refreshed"
    MISSING = "Missing"
    INVALID = "Invalid"
    EXPIRED = "Expired"
    REVOKED = "Revoked"
    REUSE_DETECTED = "ReuseDetected"
    USER_INACTIVE = "UserInactive"


class RefreshResult(CamelModel):
    outcome: RefreshOutcome
    user: AppUser | None = None
    session: UserSession | None = None

    model_config = {"arbitrary_types_allowed": True}


class SessionSummaryDto(CamelModel):
    id: UUID
    created_at: DotNetDateTime
    last_seen_at: DotNetDateTime
    expires_at: DotNetDateTime
    remember_me: bool
    user_agent: str | None
    ip_address: str | None
    is_current: bool


_ACTIVE_CHECK_TTL_SECONDS = 30
_active_cache: dict[str, tuple[bool, float]] = {}


def _cache_key(session_id: UUID) -> str:
    return f"session-active:{session_id}"


def _cache_get(key: str) -> bool | None:
    entry = _active_cache.get(key)
    if entry is None:
        return None
    value, expires_at = entry
    if time.monotonic() > expires_at:
        _active_cache.pop(key, None)
        return None
    return value


def _cache_set(key: str, value: bool) -> None:
    _active_cache[key] = (value, time.monotonic() + _ACTIVE_CHECK_TTL_SECONDS)


def _cache_evict(key: str) -> None:
    _active_cache.pop(key, None)


class SessionService:
    def __init__(
        self,
        session: AsyncSession,
        jwt: JwtTokenService | None = None,
        options: AuthSettings | None = None,
    ) -> None:
        self._session = session
        self._jwt = jwt or JwtTokenService(get_settings().auth)
        self._options = options or get_settings().auth

    @property
    def _access_cookie_name(self) -> str:
        return self._options.cookie_name or "na_auth"

    @property
    def _refresh_cookie_name(self) -> str:
        return self._options.refresh_cookie_name or "na_refresh"

    def _utcnow(self) -> datetime:
        return datetime.now(timezone.utc)

    async def start_session(
        self, user: AppUser, remember_me: bool, request: Request, response: Response
    ) -> UserSession:
        """Create a session for a fully authenticated user and write both cookies."""
        now = self._utcnow()
        raw_refresh_token = _new_refresh_token()
        session = UserSession(
            user_id=user.id,
            refresh_token_hash=_hash(raw_refresh_token),
            remember_me=remember_me,
            created_at=now,
            last_seen_at=now,
            expires_at=(
                now + timedelta(days=max(1, self._options.remember_me_days))
                if remember_me
                else now + timedelta(hours=max(1, self._options.session_hours))
            ),
            user_agent=_truncate(_user_agent(request), 400),
            ip_address=_truncate(_resolve_client_ip(request), 64),
        )
        self._session.add(session)
        await self._session.flush()
        self._write_cookies(request, response, user, session, raw_refresh_token)
        return session

    async def refresh(self, request: Request, response: Response) -> RefreshResult:
        """Exchange the refresh cookie for a new access token, rotating the token.
        A rotated-out token presented again after the grace window revokes the session."""
        raw_token = request.cookies.get(self._refresh_cookie_name)
        if not raw_token or not raw_token.strip():
            return RefreshResult(outcome=RefreshOutcome.MISSING)
        token_hash = _hash(raw_token)
        now = self._utcnow()

        session = await self._find_by_refresh_hash(token_hash)
        if session is None:
            rotated_out = await self._find_by_previous_refresh_hash(token_hash)
            if rotated_out is None:
                self.clear_cookies(request, response)
                return RefreshResult(outcome=RefreshOutcome.INVALID)
            session_row, user = rotated_out
            within_grace = (
                session_row.rotated_at is not None
                and now - session_row.rotated_at
                <= timedelta(seconds=max(0, self._options.refresh_reuse_grace_seconds))
            )
            if within_grace and _is_row_active(session_row, now) and _is_user_active(user):
                # Another tab already rotated the token; its response set the new refresh
                # cookie. Re-issue only the access token so this request can proceed.
                self._write_access_cookie(request, response, user, session_row)
                return RefreshResult(
                    outcome=RefreshOutcome.REFRESHED, user=user, session=session_row
                )
            if session_row.revoked_at is None:
                session_row.revoked_at = now
                session_row.revoked_reason = "RefreshReuse"
                await self._session.flush()
                _cache_evict(_cache_key(session_row.id))
            self.clear_cookies(request, response)
            return RefreshResult(outcome=RefreshOutcome.REUSE_DETECTED)

        session_row, user = session
        if session_row.revoked_at is not None:
            self.clear_cookies(request, response)
            return RefreshResult(outcome=RefreshOutcome.REVOKED)

        idle_limit = timedelta(days=max(1, self._options.idle_timeout_days))
        if session_row.expires_at <= now or now - session_row.last_seen_at > idle_limit:
            session_row.revoked_at = now
            session_row.revoked_reason = "Expired"
            await self._session.flush()
            _cache_evict(_cache_key(session_row.id))
            self.clear_cookies(request, response)
            return RefreshResult(outcome=RefreshOutcome.EXPIRED)

        if not _is_user_active(user):
            session_row.revoked_at = now
            session_row.revoked_reason = "UserInactive"
            await self._session.flush()
            _cache_evict(_cache_key(session_row.id))
            self.clear_cookies(request, response)
            return RefreshResult(outcome=RefreshOutcome.USER_INACTIVE)

        new_raw_token = _new_refresh_token()
        session_row.previous_refresh_token_hash = session_row.refresh_token_hash
        session_row.refresh_token_hash = _hash(new_raw_token)
        session_row.rotated_at = now
        session_row.last_seen_at = now
        session_row.user_agent = (
            _truncate(_user_agent(request), 400) or session_row.user_agent
        )
        session_row.ip_address = (
            _truncate(_resolve_client_ip(request), 64) or session_row.ip_address
        )
        await self._session.flush()
        self._write_cookies(request, response, user, session_row, new_raw_token)
        return RefreshResult(
            outcome=RefreshOutcome.REFRESHED, user=user, session=session_row
        )

    async def is_session_active(self, session_id: UUID, user_id: int) -> bool:
        """Called for every request bearing a session-scoped JWT. Cached briefly."""
        key = _cache_key(session_id)
        cached = _cache_get(key)
        if cached is not None:
            return cached
        now = self._utcnow()
        result = await self._session.execute(
            select(UserSession.id).where(
                UserSession.id == session_id,
                UserSession.user_id == user_id,
                UserSession.revoked_at.is_(None),
                UserSession.expires_at > now,
            )
        )
        active = result.first() is not None
        _cache_set(key, active)
        return active

    async def revoke(self, session_id: UUID, user_id: int, reason: str) -> bool:
        session_row = (
            await self._session.execute(
                select(UserSession).where(
                    UserSession.id == session_id, UserSession.user_id == user_id
                )
            )
        ).scalar_one_or_none()
        if session_row is None:
            return False
        if session_row.revoked_at is None:
            session_row.revoked_at = self._utcnow()
            session_row.revoked_reason = reason
            await self._session.flush()
        _cache_evict(_cache_key(session_id))
        return True

    async def revoke_all(
        self, user_id: int, except_session_id: UUID | None, reason: str
    ) -> int:
        """Revoke every active session of a user, optionally keeping one."""
        now = self._utcnow()
        stmt = select(UserSession).where(
            UserSession.user_id == user_id, UserSession.revoked_at.is_(None)
        )
        if except_session_id is not None:
            stmt = stmt.where(UserSession.id != except_session_id)
        rows = (await self._session.execute(stmt)).scalars().all()
        for row in rows:
            row.revoked_at = now
            row.revoked_reason = reason
            _cache_evict(_cache_key(row.id))
        await self._session.flush()
        return len(rows)

    async def list_active(
        self, user_id: int, current_session_id: UUID | None
    ) -> list[SessionSummaryDto]:
        now = self._utcnow()
        rows = (
            await self._session.execute(
                select(UserSession)
                .where(
                    UserSession.user_id == user_id,
                    UserSession.revoked_at.is_(None),
                    UserSession.expires_at > now,
                )
                .order_by(UserSession.last_seen_at.desc())
            )
        ).scalars().all()
        return [
            SessionSummaryDto(
                id=row.id,
                created_at=row.created_at,
                last_seen_at=row.last_seen_at,
                expires_at=row.expires_at,
                remember_me=row.remember_me,
                user_agent=row.user_agent,
                ip_address=_mask_ip(row.ip_address),
                is_current=row.id == current_session_id,
            )
            for row in rows
        ]

    async def sign_out(
        self,
        request: Request,
        response: Response,
        user_id: int | None,
        session_id: UUID | None,
    ) -> None:
        """Revoke the current session (if any) and clear both cookies."""
        if user_id is not None and session_id is not None:
            await self.revoke(session_id, user_id, "Logout")
        else:
            raw_token = request.cookies.get(self._refresh_cookie_name)
            if raw_token and raw_token.strip():
                # Access token already expired: find the session through the refresh token.
                token_hash = _hash(raw_token)
                row = (
                    await self._session.execute(
                        select(UserSession).where(
                            UserSession.refresh_token_hash == token_hash,
                            UserSession.revoked_at.is_(None),
                        )
                    )
                ).scalar_one_or_none()
                if row is not None:
                    row.revoked_at = self._utcnow()
                    row.revoked_reason = "Logout"
                    await self._session.flush()
                    _cache_evict(_cache_key(row.id))
        self.clear_cookies(request, response)

    def clear_cookies(self, request: Request, response: Response) -> None:
        secure = request.url.scheme == "https"
        response.delete_cookie(
            self._access_cookie_name,
            path="/",
            secure=secure,
            httponly=True,
            samesite="lax",
        )
        response.delete_cookie(
            self._refresh_cookie_name,
            path="/api/auth",
            secure=secure,
            httponly=True,
            samesite="strict",
        )

    async def _find_by_refresh_hash(
        self, token_hash: str
    ) -> tuple[UserSession, AppUser | None] | None:
        row = (
            await self._session.execute(
                select(UserSession).where(UserSession.refresh_token_hash == token_hash)
            )
        ).scalar_one_or_none()
        if row is None:
            return None
        return row, await self._load_user(row.user_id)

    async def _find_by_previous_refresh_hash(
        self, token_hash: str
    ) -> tuple[UserSession, AppUser | None] | None:
        row = (
            await self._session.execute(
                select(UserSession).where(
                    UserSession.previous_refresh_token_hash == token_hash
                )
            )
        ).scalar_one_or_none()
        if row is None:
            return None
        return row, await self._load_user(row.user_id)

    async def _load_user(self, user_id: int) -> AppUser | None:
        return (
            await self._session.execute(
                select(AppUser).where(AppUser.id == user_id)
            )
        ).scalar_one_or_none()

    def _write_cookies(
        self,
        request: Request,
        response: Response,
        user: AppUser,
        session: UserSession,
        raw_refresh_token: str,
    ) -> None:
        self._write_access_cookie(request, response, user, session)
        response.set_cookie(
            self._refresh_cookie_name,
            raw_refresh_token,
            httponly=True,
            secure=request.url.scheme == "https",
            # Only the SPA's own fetches to /api/auth ever need this cookie.
            samesite="strict",
            path="/api/auth",
            # Without "remember me" the cookie dies with the browser session.
            expires=session.expires_at if session.remember_me else None,
        )

    def _write_access_cookie(
        self,
        request: Request,
        response: Response,
        user: AppUser,
        session: UserSession,
    ) -> None:
        token = self._jwt.generate_token(user, session.id)
        response.set_cookie(
            self._access_cookie_name,
            token,
            httponly=True,
            secure=request.url.scheme == "https",
            samesite="lax",
            path="/",
            expires=self._jwt.get_access_token_expiration(),
        )


def _hash(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def hash_token(raw_token: str) -> str:
    """Public alias for tests (C#: SessionService.Hash)."""
    return _hash(raw_token)


def _new_refresh_token() -> str:
    return (
        base64.b64encode(secrets.token_bytes(32))
        .decode("ascii")
        .rstrip("=")
        .replace("+", "-")
        .replace("/", "_")
    )


def _is_user_active(user: AppUser | None) -> bool:
    return user is not None and user.status.lower() == "approved"


def _is_row_active(row: UserSession, now: datetime) -> bool:
    return row.revoked_at is None and row.expires_at > now


def _resolve_client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded and forwarded.strip():
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def _user_agent(request: Request) -> str | None:
    return request.headers.get("user-agent")


def _mask_ip(ip: str | None) -> str | None:
    if not ip or not ip.strip():
        return None
    parts = ip.split(".")
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.x.x"
    v6 = ip.split(":")
    return f"{v6[0]}:{v6[1]}:…" if len(v6) > 2 else ip


def _truncate(value: str | None, max_length: int) -> str | None:
    if not value or not value.strip():
        return None
    return value if len(value) <= max_length else value[:max_length]
