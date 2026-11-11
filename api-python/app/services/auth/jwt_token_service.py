"""Ported from api/Services/Auth/JwtTokenService.cs."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING
from uuid import UUID

import jwt

if TYPE_CHECKING:
    from ...models.app_user import AppUser
    from ...settings import AuthSettings


class JwtTokenService:
    def __init__(self, options: AuthSettings) -> None:
        self._options = options

    def generate_token(self, user: AppUser, session_id: UUID | None = None) -> str:
        if not self._options.jwt_signing_key or not self._options.jwt_signing_key.strip():
            raise RuntimeError("Auth:JwtSigningKey must be configured.")
        now = datetime.now(timezone.utc)
        # Claim names are what JwtSecurityTokenHandler's outbound map writes for
        # ClaimTypes.NameIdentifier/Email/Role/Name ("nameid" corroborated by
        # ai-agent/auth.py, which reads .NET-issued tokens).
        claims: dict[str, object] = {
            "nameid": str(user.id),
            "email": user.email,
            "role": user.role,
            "unique_name": user.display_name or user.email,
            "status": user.status,
        }
        if session_id is not None:
            from .current_user import SESSION_ID_CLAIM

            claims[SESSION_ID_CLAIM] = str(session_id)
            expires = self.get_access_token_expiration()
        else:
            expires = self.get_expiration()
        claims["nbf"] = now
        claims["iat"] = now
        claims["exp"] = expires
        claims["iss"] = self._options.jwt_issuer
        claims["aud"] = self._options.jwt_audience
        return jwt.encode(claims, self._options.jwt_signing_key, algorithm="HS256")

    def get_expiration(self) -> datetime:
        minutes = self._options.jwt_expiry_minutes
        if minutes <= 0:
            minutes = 720
        return datetime.now(timezone.utc) + timedelta(minutes=minutes)

    def get_access_token_expiration(self) -> datetime:
        minutes = self._options.access_token_minutes
        if minutes <= 0:
            minutes = 30
        return datetime.now(timezone.utc) + timedelta(minutes=minutes)
