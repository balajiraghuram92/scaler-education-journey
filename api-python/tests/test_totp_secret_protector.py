"""Translated from tests/StudyTracker.Api.Tests/TotpSecretProtectorTests.cs."""

from __future__ import annotations

import base64
import secrets

import pytest

from app.services.auth.totp_secret_protector import (
    TotpProtectionError,
    TotpSecretProtector,
)


def _protector() -> TotpSecretProtector:
    # 32-byte key base64 encoded
    base64_key = base64.b64encode(secrets.token_bytes(32)).decode("ascii")
    return TotpSecretProtector(base64_key, is_production=False)


def test_encrypt_and_decrypt_round_trip_preserves_exact_secret_bytes() -> None:
    protector = _protector()
    secret = secrets.token_bytes(20)
    encrypted = protector.encrypt(secret)

    assert encrypted and encrypted.strip()
    assert protector.decrypt(encrypted) == secret


def test_encrypt_produces_different_ciphertexts_due_to_random_nonce() -> None:
    protector = _protector()
    secret = secrets.token_bytes(20)
    ciphertext1 = protector.encrypt(secret)
    ciphertext2 = protector.encrypt(secret)

    assert ciphertext1 != ciphertext2
    # Both decrypt to the same secret
    assert protector.decrypt(ciphertext1) == secret
    assert protector.decrypt(ciphertext2) == secret


def test_decrypt_tampered_payload_throws_cryptographic_exception() -> None:
    protector = _protector()
    secret = secrets.token_bytes(20)
    encrypted = protector.encrypt(secret)

    payload = bytearray(base64.b64decode(encrypted))
    # Tamper with one byte in the tag portion
    payload[-1] ^= 0xFF
    tampered = base64.b64encode(bytes(payload)).decode("ascii")

    with pytest.raises(TotpProtectionError):
        protector.decrypt(tampered)


@pytest.mark.parametrize("invalid_input", ["", " ", None])
def test_decrypt_empty_or_null_throws_argument_exception(invalid_input: str | None) -> None:
    with pytest.raises(ValueError):
        _protector().decrypt(invalid_input)  # type: ignore[arg-type]


def test_decrypt_truncated_payload_throws_cryptographic_exception() -> None:
    # Nonce is 12 bytes and tag is 16 bytes = 28 bytes minimum. Anything shorter must fail.
    short_payload = base64.b64encode(bytes(20)).decode("ascii")
    with pytest.raises(TotpProtectionError):
        _protector().decrypt(short_payload)
