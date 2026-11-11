"""Ported from api/Services/Auth/CurrentUser.cs and the JWT bearer wiring in
api/Program.cs (lines 153-228).

Reads the signed-in learner from the validated JWT in the auth cookie.
Anonymous readers get nulls, which every learner-state query treats as
"no progress".
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

import jwt
from fastapi import Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_session
from ...settings import get_jwt_config

# Not "sid": the .NET JWT handler remaps that registered name on read.
SESSION_ID_CLAIM = "na_sid"

_NAMEID_ALIASES = (
    "nameid",
    "sub",
    "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/nameidentifier",
)
_ROLE_ALIASES = (
    "role",
    "http://schemas.microsoft.com/ws/2008/06/identity/claims/role",
)


@dataclass
class CurrentUser:
    user_id: int | None = None
    session_id: UUID | None = None
    is_authenticated: bool = False
    roles: tuple[str, ...] = ()

    @property
    def is_admin(self) -> bool:
        return "Admin" in self.roles


def read_user_id(claims: dict | None) -> int | None:
    if not claims:
        return None
    for alias in _NAMEID_ALIASES:
        value = claims.get(alias)
        if value is None:
            continue
        try:
            return int(str(value))
        except ValueError:
            return None
    return None


def read_session_id(claims: dict | None) -> UUID | None:
    if not claims:
        return None
    value = claims.get(SESSION_ID_CLAIM)
    if value is None:
        return None
    try:
        return UUID(str(value))
    except ValueError:
        return None


def read_roles(claims: dict | None) -> tuple[str, ...]:
    if not claims:
        return ()
    for alias in _ROLE_ALIASES:
        value = claims.get(alias)
        if value is None:
            continue
        if isinstance(value, list):
            return tuple(str(v) for v in value)
        return (str(value),)
    return ()


def decode_claims(token: str) -> dict | None:
    secret, issuer, audience, _ = get_jwt_config()
    if not secret:
        return None
    try:
        claims = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            issuer=issuer,
            audience=audience,
            leeway=0,
            options={"require": ["exp", "iss", "aud"]},
        )
        return dict(claims)
    except jwt.PyJWTError:
        return None


async def get_current_user_optional(
    request: Request, session: AsyncSession = Depends(get_session)
) -> CurrentUser:
    """Validate the JWT from the auth cookie; any failure yields anonymous."""
    _, _, _, cookie_name = get_jwt_config()
    token = request.cookies.get(cookie_name)
    if not token or not token.strip():
        return CurrentUser()
    claims = decode_claims(token)
    user_id = read_user_id(claims)
    if user_id is None:
        return CurrentUser()
    session_id = read_session_id(claims)
    if session_id is not None:
        # A session-scoped token is only valid while its session is (Program.cs
        # OnTokenValidated). Legacy tokens without the claim stay valid.
        from .session_service import SessionService

        service = SessionService(session)
        if not await service.is_session_active(session_id, user_id):
            return CurrentUser()
    return CurrentUser(
        user_id=user_id,
        session_id=session_id,
        is_authenticated=True,
        roles=read_roles(claims),
    )


async def require_user(
    current: CurrentUser = Depends(get_current_user_optional),
) -> CurrentUser:
    if not current.is_authenticated or current.user_id is None:
        # ASP.NET authorization challenge: bare 401 (with WWW-Authenticate).
        return _unauthorized()
    return current


async def require_admin(
    current: CurrentUser = Depends(get_current_user_optional),
) -> CurrentUser:
    if not current.is_authenticated or current.user_id is None:
        return _unauthorized()
    if not current.is_admin:
        # ASP.NET failed AdminOnly policy: bare 403.
        return _forbidden()
    return current


def _unauthorized() -> CurrentUser:
    raise ChallengeException(401)


def _forbidden() -> CurrentUser:
    raise ChallengeException(403)


class ChallengeException(Exception):
    def __init__(self, status: int) -> None:
        super().__init__(f"HTTP {status}")
        self.status = status


async def challenge_exception_handler(request: Request, exc: Exception) -> Response:
    if not isinstance(exc, ChallengeException):
        raise exc
    headers = {"WWW-Authenticate": "Bearer"} if exc.status == 401 else {}
    return Response(status_code=exc.status, headers=headers)
