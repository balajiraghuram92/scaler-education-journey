"""Ported from api/Services/Auth/IPasswordHasher.cs."""

from __future__ import annotations

from typing import Protocol


class IPasswordHasher(Protocol):
    def hash_password(self, password: str) -> tuple[str, str, int]:
        """Return (hash, salt, iterations). C# uses out-params; Python returns a tuple."""
        ...

    def verify_password(
        self, password: str, stored_hash: str, stored_salt: str, iterations: int
    ) -> bool:
        ...
