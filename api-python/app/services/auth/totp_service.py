"""Ported from api/Services/Auth/TotpService.cs (ITotpService + TotpService)."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time
from typing import Protocol

SECRET_SIZE_BYTES = 20  # 160 bits
PERIOD_SECONDS = 30


class ITotpService(Protocol):
    def generate_secret(self) -> bytes: ...
    def to_base32(self, secret: bytes) -> str: ...
    def build_otp_auth_uri(self, base32_secret: str, email: str) -> str: ...
    def current_counter(self) -> int: ...
    def compute_code(self, secret: bytes, counter: int) -> str: ...
    def try_verify(
        self, secret: bytes, code: str, last_accepted_counter: int | None
    ) -> tuple[bool, int]: ...


class TotpService:
    def generate_secret(self) -> bytes:
        return secrets.token_bytes(SECRET_SIZE_BYTES)

    def to_base32(self, secret: bytes) -> str:
        if not secret:
            return ""
        # Same output as the C#: RFC 4648 without padding.
        return base64.b32encode(secret).decode("ascii").rstrip("=")

    def build_otp_auth_uri(self, base32_secret: str, email: str) -> str:
        if not base32_secret or not base32_secret.strip():
            raise ValueError("base32_secret must not be empty")
        if not email or not email.strip():
            raise ValueError("email must not be empty")
        from urllib.parse import quote

        encoded_email = quote(email.strip(), safe="")
        return (
            f"otpauth://totp/Neuralascent:{encoded_email}?secret={base32_secret}"
            f"&issuer=Neuralascent&algorithm=SHA1&digits=6&period={PERIOD_SECONDS}"
        )

    def current_counter(self) -> int:
        return int(time.time()) // PERIOD_SECONDS

    def compute_code(self, secret: bytes, counter: int) -> str:
        if secret is None:
            raise ValueError("secret must not be None")
        counter_bytes = counter.to_bytes(8, "big")
        digest = hmac.new(secret, counter_bytes, hashlib.sha1).digest()
        # Dynamic truncation per RFC 4226 Section 5.3
        offset = digest[-1] & 0x0F
        binary = (
            ((digest[offset] & 0x7F) << 24)
            | ((digest[offset + 1] & 0xFF) << 16)
            | ((digest[offset + 2] & 0xFF) << 8)
            | (digest[offset + 3] & 0xFF)
        )
        return f"{binary % 1_000_000:06d}"

    def try_verify(
        self, secret: bytes, code: str, last_accepted_counter: int | None
    ) -> tuple[bool, int]:
        if not secret or not code or not code.strip():
            return False, 0
        trimmed = code.strip()
        if len(trimmed) != 6 or not trimmed.isdigit():
            return False, 0
        current = self.current_counter()
        for step in (current - 1, current, current + 1):
            # Replay protection: reject if counter was already used
            if last_accepted_counter is not None and step <= last_accepted_counter:
                continue
            expected = self.compute_code(secret, step)
            if hmac.compare_digest(expected.encode("utf-8"), trimmed.encode("utf-8")):
                return True, step
        return False, 0
