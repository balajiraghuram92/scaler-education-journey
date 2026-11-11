"""Translated from tests/StudyTracker.Api.Tests/TotpServiceTests.cs."""

from __future__ import annotations

import re

import pytest

from app.services.auth.totp_service import TotpService

_service = TotpService()


def test_generate_secret_returns_20_random_bytes() -> None:
    secret1 = _service.generate_secret()
    secret2 = _service.generate_secret()

    assert len(secret1) == 20
    assert len(secret2) == 20
    assert secret1 != secret2


@pytest.mark.parametrize(
    ("input_text", "expected_base32"),
    [
        ("", ""),
        ("f", "MY"),
        ("fo", "MZXQ"),
        ("foo", "MZXW6"),
        ("foob", "MZXW6YQ"),
        ("fooba", "MZXW6YTB"),
        ("foobar", "MZXW6YTBOI"),
    ],
)
def test_to_base32_matches_rfc4648_test_vectors_without_padding(
    input_text: str, expected_base32: str
) -> None:
    assert _service.to_base32(input_text.encode("ascii")) == expected_base32


def test_to_base32_for_20_byte_secret_produces_32_characters_without_padding() -> None:
    base32 = _service.to_base32(_service.generate_secret())

    assert len(base32) == 32
    assert "=" not in base32
    assert re.fullmatch(r"[A-Z2-7]{32}", base32)


def test_build_otp_auth_uri_contains_expected_scheme_and_parameters() -> None:
    secret = "JBSWY3DPEHPK3PXP"
    email = "learner@example.com"

    uri = _service.build_otp_auth_uri(secret, email)

    assert uri.startswith("otpauth://totp/Neuralascent:")
    assert "learner%40example.com" in uri
    assert f"secret={secret}" in uri
    assert "issuer=Neuralascent" in uri
    assert "algorithm=SHA1" in uri
    assert "digits=6" in uri
    assert "period=30" in uri


@pytest.mark.parametrize(
    ("counter", "expected_code"),
    [
        (1, "287082"),
        (37037036, "081804"),
        (37037037, "050471"),
        (41152263, "005924"),
        (66666666, "279037"),
    ],
)
def test_compute_code_matches_official_rfc6238_sha1_test_vectors(
    counter: int, expected_code: str
) -> None:
    # RFC 6238 Appendix B SHA1 key: "12345678901234567890" (20 ASCII bytes)
    rfc_secret = b"12345678901234567890"
    assert _service.compute_code(rfc_secret, counter) == expected_code


def test_try_verify_with_current_code_returns_true() -> None:
    secret = _service.generate_secret()
    current_counter = _service.current_counter()
    current_code = _service.compute_code(secret, current_counter)

    verified, accepted_counter = _service.try_verify(secret, current_code, None)

    assert verified
    assert accepted_counter == current_counter


def test_try_verify_allows_time_window_plus_minus_one() -> None:
    secret = _service.generate_secret()
    current = _service.current_counter()

    code_minus1 = _service.compute_code(secret, current - 1)
    verified1, accepted1 = _service.try_verify(secret, code_minus1, None)
    assert verified1
    assert accepted1 == current - 1

    code_plus1 = _service.compute_code(secret, current + 1)
    verified2, accepted2 = _service.try_verify(secret, code_plus1, None)
    assert verified2
    assert accepted2 == current + 1


def test_try_verify_rejects_codes_outside_window() -> None:
    secret = _service.generate_secret()
    current = _service.current_counter()

    code_minus2 = _service.compute_code(secret, current - 2)
    assert _service.try_verify(secret, code_minus2, None)[0] is False

    code_plus2 = _service.compute_code(secret, current + 2)
    assert _service.try_verify(secret, code_plus2, None)[0] is False


def test_try_verify_replay_protection_rejects_equal_or_older_accepted_counters() -> None:
    secret = _service.generate_secret()
    current = _service.current_counter()
    code = _service.compute_code(secret, current)

    # Counter already accepted at 'current'
    assert _service.try_verify(secret, code, current)[0] is False

    # Counter already accepted at future step 'current + 1'
    assert _service.try_verify(secret, code, current + 1)[0] is False

    # When previous counter was older, verification succeeds
    verified, accepted = _service.try_verify(secret, code, current - 1)
    assert verified
    assert accepted == current


@pytest.mark.parametrize("code", ["12345", "1234567", "abcdef", "", None])
def test_try_verify_invalid_input_format_returns_false(code: str | None) -> None:
    secret = _service.generate_secret()
    assert _service.try_verify(secret, code, None)[0] is False  # type: ignore[arg-type]
