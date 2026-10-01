"""Validation of .NET-issued JWTs (this service never issues tokens).

Token source: ``Authorization: Bearer <jwt>`` header, else the auth cookie.
The token must be HS256, carry ``exp``, ``iss`` and ``aud``, and match the
configured issuer/audience. Any failure is a 401 with one generic message.
"""

import jwt
from fastapi import HTTPException, Request

from config import Settings

REQUIRED_CLAIMS = ["exp", "iss", "aud"]
_UNAUTHORIZED = HTTPException(
    status_code=401,
    detail="Invalid or expired token",
    headers={"WWW-Authenticate": "Bearer"},
)


def _extract_token(request: Request, cookie_name: str) -> str | None:
    auth_header = request.headers.get("Authorization")
    if auth_header:
        scheme, _, param = auth_header.partition(" ")
        if scheme.lower() == "bearer" and param.strip():
            return param.strip()
    return request.cookies.get(cookie_name) or None


def decode_token(token: str, settings: Settings) -> dict:
    """Return the verified claims, or raise jwt.PyJWTError."""
    return jwt.decode(
        token,
        settings.jwt_signing_key,
        algorithms=["HS256"],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
        options={"require": REQUIRED_CLAIMS},
    )


def get_current_user(request: Request) -> dict:
    settings: Settings = request.app.state.settings
    token = _extract_token(request, settings.jwt_cookie_name)
    if not token:
        raise _UNAUTHORIZED
    try:
        return decode_token(token, settings)
    except jwt.PyJWTError:
        raise _UNAUTHORIZED from None


def user_id(claims: dict) -> str:
    """Stable user key from .NET claims (``nameid`` = ClaimTypes.NameIdentifier)."""
    return str(claims.get("nameid") or claims.get("sub") or "unknown")
