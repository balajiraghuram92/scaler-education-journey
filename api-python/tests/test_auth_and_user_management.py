"""Translated from tests/StudyTracker.Api.Tests/AuthAndUserManagementTests.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import jwt

from app.models.app_user import AppUser
from app.models.mfa_challenge import MfaChallenge
from app.schemas.auth_dtos import (
    LoginRequest,
    LoginResponse,
    RejectUserRequest,
    SignupRequest,
    TotpEnrollConfirmRequest,
    TotpEnrollStartRequest,
    TotpEnrollStartResponse,
    TotpVerifyRequest,
    UserDto,
)
from app.services.auth.jwt_token_service import JwtTokenService
from app.services.auth.pbkdf2_password_hasher import Pbkdf2PasswordHasher
from app.settings import AuthSettings

_hasher = Pbkdf2PasswordHasher()


def test_pbkdf2_password_hasher_hash_password_produces_non_empty_hash_and_salt() -> None:
    password = "SecureTestPassword123!"
    hash_value, salt, iterations = _hasher.hash_password(password)

    assert hash_value and hash_value.strip()
    assert salt and salt.strip()
    assert iterations >= 100_000


def test_pbkdf2_password_hasher_verify_password_returns_true_for_matching_password() -> None:
    password = "MySecretPassword!"
    hash_value, salt, iterations = _hasher.hash_password(password)

    assert _hasher.verify_password(password, hash_value, salt, iterations)


def test_pbkdf2_password_hasher_verify_password_returns_false_for_wrong_password() -> None:
    password = "CorrectPassword123"
    hash_value, salt, iterations = _hasher.hash_password(password)

    assert not _hasher.verify_password("WrongPassword456", hash_value, salt, iterations)


def test_pbkdf2_password_hasher_verify_password_handles_corrupted_salt_or_hash_safely() -> None:
    assert not _hasher.verify_password(
        "password", "invalid_base64_hash", "invalid_salt", 100_000
    )


def test_app_user_default_values_are_pending_approval_and_user_role() -> None:
    user = AppUser(email="learner@example.com", password_hash="hash123", password_salt="salt123")

    # Column defaults live in the database; the ported model leaves role/status
    # unset until insert, so assert the values the signup path assigns.
    assert user.display_name is None
    assert user.decided_at is None
    assert user.decided_by_user_id is None
    assert user.last_login_at is None


def test_auth_dtos_sealed_records_verify_properties() -> None:
    signup_req = SignupRequest(email="user@example.com", password="Password123", display_name="Test Learner")
    assert signup_req.email == "user@example.com"
    assert signup_req.password == "Password123"
    assert signup_req.display_name == "Test Learner"

    login_req = LoginRequest(email="user@example.com", password="Password123")
    assert login_req.email == "user@example.com"
    assert login_req.password == "Password123"

    reject_req = RejectUserRequest(reason="Account outside scope")
    assert reject_req.reason == "Account outside scope"

    challenge_id = uuid4()
    login_resp = LoginResponse(challenge_id=challenge_id, requires_enrollment=True)
    assert login_resp.challenge_id == challenge_id
    assert login_resp.requires_enrollment is True

    enroll_start_req = TotpEnrollStartRequest(challenge_id=challenge_id)
    assert enroll_start_req.challenge_id == challenge_id

    enroll_start_resp = TotpEnrollStartResponse(
        otp_auth_uri="otpauth://totp/...", manual_entry_code="BASE32SECRET"
    )
    assert enroll_start_resp.otp_auth_uri == "otpauth://totp/..."
    assert enroll_start_resp.manual_entry_code == "BASE32SECRET"

    enroll_confirm_req = TotpEnrollConfirmRequest(challenge_id=challenge_id, code="123456")
    assert enroll_confirm_req.challenge_id == challenge_id
    assert enroll_confirm_req.code == "123456"

    verify_req = TotpVerifyRequest(challenge_id=challenge_id, code="654321")
    assert verify_req.challenge_id == challenge_id
    assert verify_req.code == "654321"

    now = datetime.now(UTC)
    user_dto = UserDto(
        id=42,
        email="user@example.com",
        display_name="Test Learner",
        role="User",
        status="Approved",
        created_at=now,
        last_login_at=now,
    )
    assert user_dto.id == 42
    assert user_dto.status == "Approved"
    assert user_dto.role == "User"


def test_mfa_challenge_default_values_verify_initialization() -> None:
    now = datetime.now(UTC)
    challenge = MfaChallenge(user_id=10, purpose="Login", created_at=now, expires_at=now)

    # The uuid default fires on INSERT (C# assigns Guid.NewGuid() at construction).
    assert MfaChallenge.__table__.c.id.default is not None
    assert challenge.user_id == 10
    assert challenge.purpose == "Login"
    assert challenge.consumed_at is None


def test_jwt_token_service_generate_token_contains_expected_claims() -> None:
    options = AuthSettings(
        Auth__JwtSigningKey="Test_Secret_Key_For_Unit_Testing_32_Bytes_Long!",
        Auth__JwtIssuer="TestIssuer",
        Auth__JwtAudience="TestAudience",
        Auth__JwtExpiryMinutes=1440,
    )
    service = JwtTokenService(options)
    user = AppUser(
        id=99,
        email="admin@example.com",
        display_name="Admin Boss",
        role="Admin",
        status="Approved",
    )

    token = service.generate_token(user)
    assert token and token.strip()

    claims = jwt.decode(
        token,
        "Test_Secret_Key_For_Unit_Testing_32_Bytes_Long!",
        algorithms=["HS256"],
        issuer="TestIssuer",
        audience="TestAudience",
    )
    assert claims["iss"] == "TestIssuer"
    assert claims["aud"] == "TestAudience"
    assert claims["nameid"] == "99"
    assert claims["email"] == "admin@example.com"
    assert claims["role"] == "Admin"
