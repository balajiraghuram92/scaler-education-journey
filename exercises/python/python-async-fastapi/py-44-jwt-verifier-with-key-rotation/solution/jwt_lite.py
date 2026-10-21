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


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64u_decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def _json(obj: dict[str, Any]) -> bytes:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode()


class JwtCodec:
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
        if active_kid not in keys:
            raise ValueError("active_kid must be present in keys")
        self._keys = dict(keys)
        self._active_kid = active_kid
        self._issuer = issuer
        self._audience = audience
        self._leeway = leeway_s
        self._clock = clock

    def _mac(self, kid: str, signing_input: str) -> bytes:
        return hmac.new(self._keys[kid], signing_input.encode(), hashlib.sha256).digest()

    def issue(self, sub: str, scopes: list[str], ttl_s: int = 900) -> str:
        now = int(self._clock())
        header = {"alg": "HS256", "typ": "JWT", "kid": self._active_kid}
        claims = {
            "sub": sub,
            "iss": self._issuer,
            "aud": self._audience,
            "iat": now,
            "exp": now + ttl_s,
            "scope": " ".join(scopes),
        }
        signing_input = f"{_b64u(_json(header))}.{_b64u(_json(claims))}"
        return f"{signing_input}.{_b64u(self._mac(self._active_kid, signing_input))}"

    def verify(self, token: str) -> Principal:
        try:
            head_b64, body_b64, sig_b64 = token.split(".")
            header = json.loads(_b64u_decode(head_b64))
            claims = json.loads(_b64u_decode(body_b64))
            signature = _b64u_decode(sig_b64)
        except (ValueError, TypeError) as exc:
            raise Unauthorized("malformed") from exc
        if not isinstance(header, dict) or not isinstance(claims, dict):
            raise Unauthorized("malformed")
        if header.get("alg") != "HS256":
            raise Unauthorized("alg")
        kid = header.get("kid")
        if kid not in self._keys:
            raise Unauthorized("kid")
        if not hmac.compare_digest(self._mac(kid, f"{head_b64}.{body_b64}"), signature):
            raise Unauthorized("signature")
        for name in ("sub", "iss", "aud", "exp", "iat"):
            if name not in claims:
                raise Unauthorized(f"missing {name}")
        now = self._clock()
        if claims["iss"] != self._issuer:
            raise Unauthorized("issuer")
        audiences = claims["aud"] if isinstance(claims["aud"], list) else [claims["aud"]]
        if self._audience not in audiences:
            raise Unauthorized("audience")
        if claims["exp"] <= now - self._leeway:
            raise Unauthorized("expired")
        if "nbf" in claims and claims["nbf"] > now + self._leeway:
            raise Unauthorized("not yet valid")
        scopes = frozenset(str(claims.get("scope", "")).split())
        return Principal(sub=str(claims["sub"]), scopes=scopes, claims=claims)


def require_scopes(principal: Principal, *required: str) -> None:
    missing = sorted(set(required) - principal.scopes)
    if missing:
        raise Forbidden("missing scope: " + " ".join(missing))
