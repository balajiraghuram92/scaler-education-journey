"""Ported from api/Services/Auth/TotpSecretProtector.cs."""

from __future__ import annotations

import base64
import hashlib
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE_BYTES = 12
TAG_SIZE_BYTES = 16


class TotpProtectionError(Exception):
    pass


def derive_key(raw_key: str, is_production: bool) -> bytes:
    if not raw_key or not raw_key.strip():
        if is_production:
            raise TotpProtectionError(
                "Production configuration error: Auth:TotpEncryptionKey must be set."
            )
        # Local-dev-only convenience: a fresh random key each process start.
        print(
            "WARNING: Auth:TotpEncryptionKey not configured — using an ephemeral random "
            "dev-only key. Set Auth__TotpEncryptionKey for any shared or persistent environment."
        )
        return secrets.token_bytes(32)
    try:
        decoded = base64.b64decode(raw_key, validate=True)
    except ValueError:
        return hashlib.sha256(raw_key.encode("utf-8")).digest()
    if len(decoded) == 32:
        return decoded
    return hashlib.sha256(decoded).digest()


class TotpSecretProtector:
    def __init__(self, raw_key: str, is_production: bool = False) -> None:
        self._key = derive_key(raw_key, is_production)
        self._aesgcm = AESGCM(self._key)

    def encrypt(self, raw_secret: bytes) -> str:
        if raw_secret is None:
            raise ValueError("raw_secret must not be None")
        nonce = secrets.token_bytes(NONCE_SIZE_BYTES)
        # cryptography appends the 16-byte tag to the ciphertext.
        ciphertext_and_tag = self._aesgcm.encrypt(nonce, raw_secret, None)
        # payload = nonce (12 bytes) || ciphertext (variable) || tag (16 bytes)
        payload = nonce + ciphertext_and_tag
        return base64.b64encode(payload).decode("ascii")

    def decrypt(self, encrypted: str) -> bytes:
        if not encrypted or not encrypted.strip():
            raise ValueError("encrypted must not be empty")
        try:
            payload = base64.b64decode(encrypted, validate=True)
        except ValueError as exc:
            raise TotpProtectionError("Encrypted TOTP secret payload is not valid base64.") from exc
        if len(payload) < NONCE_SIZE_BYTES + TAG_SIZE_BYTES:
            raise TotpProtectionError(
                "Encrypted TOTP secret payload is malformed or too short."
            )
        nonce = payload[:NONCE_SIZE_BYTES]
        ciphertext_and_tag = payload[NONCE_SIZE_BYTES:]
        try:
            return self._aesgcm.decrypt(nonce, ciphertext_and_tag, None)
        except InvalidTag as exc:
            raise TotpProtectionError("Encrypted TOTP secret failed authentication.") from exc
