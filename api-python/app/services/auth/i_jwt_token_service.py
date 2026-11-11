"""Ported from api/Services/Auth/IJwtTokenService.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Protocol
from uuid import UUID

if TYPE_CHECKING:
    from ...models.app_user import AppUser


class IJwtTokenService(Protocol):
    def generate_token(self, user: AppUser, session_id: UUID | None = None) -> str:
        """Issue an access token. With a session id the token is short-lived and
        carries the session claim; without one it uses the legacy long expiry
        (CLI/tests only)."""
        ...

    def get_expiration(self) -> datetime:
        ...

    def get_access_token_expiration(self) -> datetime:
        ...
