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


@dataclass
class _Record:
    family: str
    user: str
    issued_at: float
    rotated_at: float | None = None


class RefreshTokenService:
    def __init__(
        self,
        *,
        ttl_s: float = 7 * 86400,
        family_max_age_s: float = 30 * 86400,
        grace_s: float = 0.0,
        clock: Callable[[], float] = time.time,
    ) -> None:
        self._ttl = ttl_s
        self._family_max_age = family_max_age_s
        self._grace = grace_s
        self._clock = clock
        self._lock = threading.Lock()
        self._records: dict[str, _Record] = {}
        self._family_started: dict[str, float] = {}
        self._revoked: set[str] = set()

    @staticmethod
    def _digest(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def _mint(self, family: str, user: str, now: float) -> str:
        token = secrets.token_urlsafe(32)
        self._records[self._digest(token)] = _Record(family, user, now)
        return token

    def login(self, user: str) -> str:
        now = self._clock()
        with self._lock:
            family = secrets.token_hex(8)
            self._family_started[family] = now
            return self._mint(family, user, now)

    def rotate(self, token: str) -> str:
        now = self._clock()
        with self._lock:
            rec = self._records.get(self._digest(token))
            if rec is None or rec.family in self._revoked:
                raise InvalidRefreshToken("invalid")
            if now - rec.issued_at >= self._ttl or now - self._family_started[rec.family] >= self._family_max_age:
                raise InvalidRefreshToken("expired")
            if rec.rotated_at is not None:
                if now - rec.rotated_at < self._grace:
                    raise GraceReuse("token already rotated; retry with the newest token")
                self._revoked.add(rec.family)
                raise ReuseDetected("rotated token replayed; family revoked")
            rec.rotated_at = now
            return self._mint(rec.family, rec.user, now)

    def revoke_user(self, user: str) -> int:
        with self._lock:
            families = {r.family for r in self._records.values() if r.user == user}
            self._revoked |= families
            return len(families)
