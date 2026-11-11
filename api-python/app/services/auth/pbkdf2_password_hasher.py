"""Ported from api/Services/Auth/Pbkdf2PasswordHasher.cs."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

DEFAULT_ITERATIONS = 210_000
SALT_SIZE_BYTES = 16
HASH_SIZE_BYTES = 32


def hash_password(password: str) -> tuple[str, str, int]:
    if not password or not password.strip():
        raise ValueError("password must not be empty")
    salt_bytes = secrets.token_bytes(SALT_SIZE_BYTES)
    iterations = DEFAULT_ITERATIONS
    hash_bytes = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt_bytes, iterations, HASH_SIZE_BYTES
    )
    salt = base64.b64encode(salt_bytes).decode("ascii")
    return base64.b64encode(hash_bytes).decode("ascii"), salt, iterations


def verify_password(
    password: str, stored_hash: str, stored_salt: str, iterations: int
) -> bool:
    if not password or not password.strip():
        return False
    if not stored_hash or not stored_hash.strip():
        return False
    if not stored_salt or not stored_salt.strip():
        return False
    try:
        salt_bytes = base64.b64decode(stored_salt, validate=True)
        expected = base64.b64decode(stored_hash, validate=True)
    except ValueError:
        return False
    actual = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt_bytes,
        iterations if iterations > 0 else DEFAULT_ITERATIONS,
        len(expected),
    )
    return hmac.compare_digest(actual, expected)


class Pbkdf2PasswordHasher:
    """Ported from api/Services/Auth/Pbkdf2PasswordHasher.cs (instance wrapper)."""

    default_iterations = DEFAULT_ITERATIONS
    salt_size_bytes = SALT_SIZE_BYTES
    hash_size_bytes = HASH_SIZE_BYTES

    def hash_password(self, password: str) -> tuple[str, str, int]:
        return hash_password(password)

    def verify_password(
        self, password: str, stored_hash: str, stored_salt: str, iterations: int
    ) -> bool:
        return verify_password(password, stored_hash, stored_salt, iterations)
