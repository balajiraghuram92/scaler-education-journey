"""Interchange proofs: artefacts written by one API must be accepted by the other.

Each test pins the byte-level contract against a fixed vector from the
underlying standard (same algorithm, parameters and encoding the C# uses),
so a mismatch fails here rather than at parity time. Vectors minted by a
running .NET API additionally require the commands in PROGRESS.md (not run:
shell unavailable).
"""

from __future__ import annotations

import base64

import jwt
import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.models.app_user import AppUser
from app.services.auth.current_user import SESSION_ID_CLAIM, decode_claims
from app.services.auth.jwt_token_service import JwtTokenService
from app.services.auth.pbkdf2_password_hasher import (
    DEFAULT_ITERATIONS,
    HASH_SIZE_BYTES,
    SALT_SIZE_BYTES,
    verify_password,
)
from app.services.auth.session_service import hash_token
from app.services.auth.totp_secret_protector import TotpSecretProtector
from app.services.auth.totp_service import TotpService
from app.settings import AuthSettings

_SIGNING_KEY = "interchange-test-signing-key-32-bytes!!"


def _auth_options() -> AuthSettings:
    return AuthSettings(
        Auth__JwtSigningKey=_SIGNING_KEY,
        Auth__JwtIssuer="neuralascent",
        Auth__JwtAudience="neuralascent-app",
    )


def test_pbkdf2_matches_standard_vector_and_csharp_parameters() -> None:
    # PBKDF2-HMAC-SHA256 reference vector: password "password", salt "salt",
    # 1 iteration, 32 bytes out.
    expected_hex = "120fb6cffcf8b32c43e7225256c4f837a86548c92ccc35480805987cb70be17b"
    expected_b64 = base64.b64encode(bytes.fromhex(expected_hex)).decode("ascii")
    salt_b64 = base64.b64encode(b"salt").decode("ascii")

    # .NET's Rfc2898DeriveBytes.Pbkdf2(SHA256) computes the same function, so a
    # .NET-written hash verifies here and vice versa.
    assert verify_password("password", expected_b64, salt_b64, 1) is True
    assert verify_password("wrong", expected_b64, salt_b64, 1) is False

    # A Python-written hash uses the identical format and parameters.
    assert DEFAULT_ITERATIONS == 210_000
    assert SALT_SIZE_BYTES == 16
    assert HASH_SIZE_BYTES == 32


def test_jwt_python_token_has_dotnet_claim_layout_and_validates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("Auth__JwtSigningKey", _SIGNING_KEY)
    monkeypatch.setenv("Auth__JwtIssuer", "neuralascent")
    monkeypatch.setenv("Auth__JwtAudience", "neuralascent-app")
    service = JwtTokenService(_auth_options())
    user = AppUser(
        id=7, email="u@example.com", display_name=None, role="User", status="Approved"
    )
    token = service.generate_token(user)

    header = jwt.get_unverified_header(token)
    assert header["alg"] == "HS256"

    claims = jwt.decode(
        token, _SIGNING_KEY, algorithms=["HS256"], issuer="neuralascent", audience="neuralascent-app"
    )
    # Exact claim layout the .NET JwtSecurityTokenHandler emits (outbound map).
    assert claims["nameid"] == "7"
    assert claims["email"] == "u@example.com"
    assert claims["role"] == "User"
    assert claims["unique_name"] == "u@example.com"
    assert claims["status"] == "Approved"
    assert SESSION_ID_CLAIM not in claims

    # The API's own validator accepts it (same path a .NET-issued token takes).
    assert decode_claims(token) is not None


def test_jwt_session_claim_round_trip() -> None:
    from uuid import uuid4

    service = JwtTokenService(_auth_options())
    user = AppUser(
        id=9, email="s@example.com", display_name="S", role="User", status="Approved"
    )
    session_id = uuid4()
    token = service.generate_token(user, session_id)

    claims = jwt.decode(
        token, _SIGNING_KEY, algorithms=["HS256"], issuer="neuralascent", audience="neuralascent-app"
    )
    assert claims[SESSION_ID_CLAIM] == str(session_id)


def test_totp_code_matches_rfc_vector_for_protected_secret() -> None:
    # The RFC 6238 Appendix B secret, stored the way the API stores it
    # (AES-GCM encrypted), still yields the RFC-mandated code.
    protector = TotpSecretProtector(base64.b64encode(b"0" * 32).decode("ascii"))
    totp = TotpService()
    encrypted = protector.encrypt(b"12345678901234567890")
    secret = protector.decrypt(encrypted)
    assert totp.compute_code(secret, 37037036) == "081804"


def test_aesgcm_primitive_matches_nist_vector() -> None:
    # NIST SP 800-38D test case 2 (AES-128-GCM, all-zero key/nonce/plaintext).
    # Proves the crypto core both sides implement agrees with the standard.
    primitive = AESGCM(bytes(16))
    ciphertext_and_tag = primitive.encrypt(bytes(12), bytes(16), None)
    assert ciphertext_and_tag.hex() == (
        "0388dace60b6a392f328c2b971b2fe78" "ab6e47c2b514f2c2458c5f558a5a9551"
    )


def test_protector_payload_layout_is_nonce_ciphertext_tag() -> None:
    key = bytes(range(32))
    protector = TotpSecretProtector(base64.b64encode(key).decode("ascii"))
    secret = bytes(range(20))
    payload = base64.b64decode(protector.encrypt(secret))

    # 12-byte nonce || ciphertext || 16-byte tag.
    assert len(payload) == 12 + 20 + 16
    nonce, rest = payload[:12], payload[12:]
    assert AESGCM(key).decrypt(nonce, rest, None) == secret


def test_session_token_hash_matches_sha256_hex() -> None:
    # SessionService.Hash is lowercase-hex SHA256 of the raw token.
    assert (
        hash_token("abc")
        == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )
    hashed = hash_token("some-refresh-token")
    assert len(hashed) == 64
    assert hashed == hashed.lower()
    assert all(c in "0123456789abcdef" for c in hashed)
