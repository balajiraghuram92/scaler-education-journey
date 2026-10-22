from __future__ import annotations

import hashlib
import secrets
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass


class InvalidRefreshToken(Exception):
    """Unknown, expired or revoked token."""


class ReuseDetected(InvalidRefreshToken):
    """A rotated token was replayed outside the grace window; the family is revoked."""


class GraceReuse(InvalidRefreshToken):
    """A rotated token was replayed inside the grace window; nothing is revoked."""


class RefreshTokenService:
    """Server-side refresh-token rotation. Keep everything framework-free and clock-injectable.

    State rules:
    - only the SHA-256 hex digest of a token is stored; a plaintext token never appears in any
      internal dictionary
    - every state change happens under one ``threading.Lock`` so check-and-flip is atomic
    """

    def __init__(
        self,
        *,
        ttl_s: float = 7 * 86400,
        family_max_age_s: float = 30 * 86400,
        grace_s: float = 0.0,
        clock: Callable[[], float] = time.time,
    ) -> None:
        raise NotImplementedError("Implement __init__")

    def login(self, user: str) -> str:
        """Start a new token family for ``user`` and return a new ``secrets.token_urlsafe(32)`` token."""
        raise NotImplementedError("Implement login")

    def rotate(self, token: str) -> str:
        """Return a new token in the same family and mark the presented token rotated.

        - unknown token or revoked family: ``InvalidRefreshToken("invalid")``
        - token older than ``ttl_s`` or family older than ``family_max_age_s``:
          ``InvalidRefreshToken("expired")``
        - an already-rotated token presented within ``grace_s`` seconds of its rotation:
          ``GraceReuse`` (revokes nothing)
        - an already-rotated token presented after the grace window: ``ReuseDetected`` and the
          whole family is revoked (with ``grace_s=0`` any replay is ``ReuseDetected``)
        """
        raise NotImplementedError("Implement rotate")

    def revoke_user(self, user: str) -> int:
        """Revoke every family belonging to ``user``; return the number of families."""
        raise NotImplementedError("Implement revoke_user")
