from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


class Unauthorized(Exception):
    """Identity could not be established (HTTP 401)."""


class Forbidden(Exception):
    """Identity known but not permitted (HTTP 403)."""


@dataclass(frozen=True)
class Principal:
    sub: str
    scopes: frozenset[str]
    claims: dict[str, Any] = field(default_factory=dict, compare=False)


class JwtCodec:
    """Issues and verifies HS256 JWTs. The algorithm is never taken from the token header."""

    def __init__(
        self,
        keys: dict[str, bytes],
        *,
        active_kid: str,
        issuer: str,
        audience: str,
        leeway_s: int = 0,
        clock: Callable[[], float] = time.time,
    ) -> None:
        """``keys`` maps ``kid`` to key bytes. ``active_kid`` signs new tokens and must be a key
        in ``keys``, otherwise raise ``ValueError``."""
        raise NotImplementedError("Implement __init__")

    def issue(self, sub: str, scopes: list[str], ttl_s: int = 900) -> str:
        """Return a compact JWT (base64url without padding, three dot-separated segments).

        Header: ``{"alg": "HS256", "typ": "JWT", "kid": <active kid>}``.
        Claims: ``sub``, ``iss``, ``aud``, ``iat``, ``exp`` (= iat + ttl_s) and ``scope``
        (space-separated).
        """
        raise NotImplementedError("Implement issue")

    def verify(self, token: str) -> Principal:
        """Return a ``Principal`` or raise ``Unauthorized`` with one of these short reasons:

        - ``malformed``: wrong segment count, bad base64 or JSON, header or claims not an object
        - ``alg``: anything other than HS256, including ``none``
        - ``kid``: unknown key id
        - ``signature``: compare with ``hmac.compare_digest``
        - ``missing <claim>`` for each of sub, iss, aud, exp, iat
        - ``issuer`` / ``audience`` mismatch (the ``aud`` claim may be a string or a list)
        - ``expired``: ``exp <= now - leeway``
        - ``not yet valid``: ``nbf > now + leeway`` (nbf is optional)
        """
        raise NotImplementedError("Implement verify")


def require_scopes(principal: Principal, *required: str) -> None:
    """Raise ``Forbidden("missing scope: a b")`` listing the missing scopes in sorted order."""
    raise NotImplementedError("Implement require_scopes")
