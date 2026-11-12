"""Ported from api/Endpoints/AuthEndpoints.cs."""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..errors import endpoint_problem
from ..models.app_user import AppUser
from ..models.mfa_challenge import MfaChallenge
from ..rate_limit import require_auth_policy, require_refresh_policy
from ..schemas.auth_dtos import (
    LoginRequest,
    LoginResponse,
    SignupRequest,
    TotpEnrollConfirmRequest,
    TotpEnrollStartRequest,
    TotpEnrollStartResponse,
    TotpVerifyRequest,
    UserDto,
)
from ..services.auth.current_user import (
    CurrentUser,
    get_current_user_optional,
    require_user,
)
from ..services.auth.pbkdf2_password_hasher import Pbkdf2PasswordHasher
from ..services.auth.session_service import RefreshOutcome, SessionService
from ..services.auth.totp_secret_protector import TotpSecretProtector
from ..services.auth.totp_service import TotpService
from ..services.email.smtp_email_notification_service import (
    SmtpEmailNotificationService,
)
from ..settings import get_environment, get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", re.IGNORECASE)

_password_hasher = Pbkdf2PasswordHasher()
_totp_service = TotpService()


def _protector() -> TotpSecretProtector:
    settings = get_settings()
    return TotpSecretProtector(
        settings.auth.totp_encryption_key,
        is_production=get_environment().lower() == "production",
    )


def _email_service() -> SmtpEmailNotificationService:
    settings = get_settings()
    return SmtpEmailNotificationService(settings.email, settings.smtp)


def _user_dto(user: AppUser) -> UserDto:
    return UserDto(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        status=user.status,
        created_at=user.created_at,
        last_login_at=user.last_login_at,
    )


def _utcnow() -> datetime:
    return datetime.now(UTC)


async def _load_challenge_with_user(
    session: AsyncSession, challenge_id: UUID | None
) -> tuple[MfaChallenge, AppUser | None] | None:
    challenge = (
        await session.execute(
            select(MfaChallenge).where(MfaChallenge.id == challenge_id)
        )
    ).scalar_one_or_none()
    if challenge is None:
        return None
    user = (
        await session.execute(select(AppUser).where(AppUser.id == challenge.user_id))
    ).scalar_one_or_none()
    return challenge, user


@router.post("/signup", dependencies=[Depends(require_auth_policy)])
async def signup(
    body: SignupRequest,
    background: BackgroundTasks,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    if not body.email or not body.email.strip() or not _EMAIL_RE.match(body.email.strip()):
        return endpoint_problem(request, 400, "Invalid email.", "A valid email address is required.")
    min_length = get_settings().auth.min_password_length
    if min_length <= 0:
        min_length = 10
    if not body.password or not body.password.strip() or len(body.password) < min_length:
        return endpoint_problem(
            request,
            400,
            "Invalid password.",
            f"Password must be at least {min_length} characters in length.",
        )
    normalized_email = body.email.strip().lower()
    exists = (
        await session.execute(
            select(AppUser.id).where(func.lower(AppUser.email) == normalized_email)
        )
    ).first()
    if exists is not None:
        # Enumeration attack protection: return uniform generic success message
        # without leaking account existence
        return {
            "message": "Registration request received. If eligible, your account will be reviewed by an administrator."
        }
    password_hash, salt, iterations = _password_hasher.hash_password(body.password)
    new_user = AppUser(
        email=normalized_email,
        password_hash=password_hash,
        password_salt=salt,
        password_iterations=iterations,
        role="User",
        status="PendingApproval",
        display_name=body.display_name.strip() if body.display_name and body.display_name.strip() else None,
        created_at=_utcnow(),
        totp_enabled=False,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    # Asynchronous notifications to admin and user (C# discards the tasks).
    email_service = _email_service()
    background.add_task(email_service.send_admin_new_user_alert, new_user)
    background.add_task(email_service.send_user_pending_confirmation, new_user)
    return {
        "message": "Registration request received. If eligible, your account will be reviewed by an administrator."
    }


@router.post(
    "/login", response_model=LoginResponse, dependencies=[Depends(require_auth_policy)]
)
async def login(
    body: LoginRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    if not body.email or not body.email.strip() or not body.password or not body.password.strip():
        return endpoint_problem(
            request, 400, "Invalid credentials.", "Email and password are required."
        )
    normalized_email = body.email.strip().lower()
    user = (
        await session.execute(
            select(AppUser).where(func.lower(AppUser.email) == normalized_email)
        )
    ).scalar_one_or_none()
    if user is None:
        return endpoint_problem(
            request, 401, "Invalid credentials.", "The email or password entered is incorrect."
        )
    if not _password_hasher.verify_password(
        body.password, user.password_hash, user.password_salt, user.password_iterations
    ):
        return endpoint_problem(
            request, 401, "Invalid credentials.", "The email or password entered is incorrect."
        )
    if user.status.lower() == "pendingapproval":
        return endpoint_problem(
            request,
            403,
            "Account Pending Approval",
            "Your registration is pending administrator approval. You will receive an email once approved.",
        )
    if user.status.lower() == "rejected":
        return endpoint_problem(
            request,
            403,
            "Registration Rejected",
            "Your registration was not approved by an administrator.",
        )
    if user.status.lower() == "disabled" or user.status.lower() != "approved":
        return endpoint_problem(
            request,
            403,
            "Account Inactive",
            "Your account is inactive or disabled. Please contact an administrator.",
        )
    # Two-factor authentication handshake: do NOT set session cookie here.
    # Return a single-purpose challenge ID backed by an mfa_challenge record.
    now = _utcnow()
    challenge = MfaChallenge(
        user_id=user.id,
        purpose="Login" if user.totp_enabled else "Enrollment",
        created_at=now,
        expires_at=now + timedelta(minutes=5),
        failed_attempts=0,
    )
    session.add(challenge)
    await session.commit()
    await session.refresh(challenge)
    return LoginResponse(challenge_id=challenge.id, requires_enrollment=not user.totp_enabled)


@router.post("/totp/enroll/start", response_model=TotpEnrollStartResponse)
async def totp_enroll_start(
    body: TotpEnrollStartRequest,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    loaded = await _load_challenge_with_user(session, body.challenge_id)
    if loaded is None:
        return endpoint_problem(
            request,
            400,
            "Invalid or expired MFA challenge.",
            "The MFA challenge is invalid, expired, or has already been used. Please log in again.",
        )
    challenge, user = loaded
    if (
        challenge.consumed_at is not None
        or challenge.expires_at <= _utcnow()
        or challenge.purpose != "Enrollment"
    ):
        return endpoint_problem(
            request,
            400,
            "Invalid or expired MFA challenge.",
            "The MFA challenge is invalid, expired, or has already been used. Please log in again.",
        )
    if user is None or user.status.lower() != "approved":
        return endpoint_problem(
            request, 401, "Unauthorized.", "User account is invalid or unapproved."
        )
    raw_secret = _totp_service.generate_secret()
    base32_secret = _totp_service.to_base32(raw_secret)
    user.totp_secret_encrypted = _protector().encrypt(raw_secret)
    await session.commit()
    otp_auth_uri = _totp_service.build_otp_auth_uri(base32_secret, user.email)
    return TotpEnrollStartResponse(otp_auth_uri=otp_auth_uri, manual_entry_code=base32_secret)


@router.post(
    "/totp/enroll/confirm",
    response_model=UserDto,
    dependencies=[Depends(require_auth_policy)],
)
async def totp_enroll_confirm(
    body: TotpEnrollConfirmRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    if not body.code or not body.code.strip():
        return endpoint_problem(
            request, 400, "Verification code required.", "A 6-digit TOTP code is required."
        )
    loaded = await _load_challenge_with_user(session, body.challenge_id)
    if loaded is None:
        return _bad_challenge(request)
    challenge, user = loaded
    if (
        challenge.consumed_at is not None
        or challenge.expires_at <= _utcnow()
        or challenge.purpose != "Enrollment"
    ):
        return _bad_challenge(request)
    if challenge.failed_attempts >= 5:
        challenge.consumed_at = _utcnow()
        await session.commit()
        return endpoint_problem(
            request,
            400,
            "Too many failed attempts.",
            "Maximum verification attempts reached. Please restart login.",
        )
    if (
        user is None
        or user.status.lower() != "approved"
        or not user.totp_secret_encrypted
        or not user.totp_secret_encrypted.strip()
    ):
        return endpoint_problem(
            request,
            401,
            "Unauthorized.",
            "User account is invalid or enrollment has not been initialized.",
        )
    try:
        secret = _protector().decrypt(user.totp_secret_encrypted)
    except Exception:
        return endpoint_problem(
            request, 500, "Decryption error.", "Failed to decrypt TOTP secret."
        )
    verified, accepted_counter = _totp_service.try_verify(
        secret, body.code, user.last_accepted_totp_counter
    )
    if not verified:
        challenge.failed_attempts += 1
        if challenge.failed_attempts >= 5:
            challenge.consumed_at = _utcnow()
        await session.commit()
        return endpoint_problem(
            request,
            400,
            "Invalid code.",
            "The 6-digit verification code is invalid or has expired.",
        )
    # Enrollment confirmed: mark TOTP enabled, record counter, update last login, consume challenge
    user.totp_enabled = True
    user.last_accepted_totp_counter = accepted_counter
    user.last_login_at = _utcnow()
    challenge.consumed_at = _utcnow()
    await session.flush()
    await SessionService(session).start_session(user, body.remember_me, request, response)
    await session.commit()
    return _user_dto(user)


@router.post(
    "/totp/verify", response_model=UserDto, dependencies=[Depends(require_auth_policy)]
)
async def totp_verify(
    body: TotpVerifyRequest,
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    if not body.code or not body.code.strip():
        return endpoint_problem(
            request, 400, "Verification code required.", "A 6-digit TOTP code is required."
        )
    loaded = await _load_challenge_with_user(session, body.challenge_id)
    if loaded is None:
        return _bad_challenge(request)
    challenge, user = loaded
    if (
        challenge.consumed_at is not None
        or challenge.expires_at <= _utcnow()
        or challenge.purpose != "Login"
    ):
        return _bad_challenge(request)
    if challenge.failed_attempts >= 5:
        challenge.consumed_at = _utcnow()
        await session.commit()
        return endpoint_problem(
            request,
            400,
            "Too many failed attempts.",
            "Maximum verification attempts reached. Please restart login.",
        )
    if (
        user is None
        or user.status.lower() != "approved"
        or not user.totp_enabled
        or not user.totp_secret_encrypted
        or not user.totp_secret_encrypted.strip()
    ):
        return endpoint_problem(
            request, 401, "Unauthorized.", "User account is invalid or TOTP is not enabled."
        )
    try:
        secret = _protector().decrypt(user.totp_secret_encrypted)
    except Exception:
        return endpoint_problem(
            request, 500, "Decryption error.", "Failed to decrypt TOTP secret."
        )
    verified, accepted_counter = _totp_service.try_verify(
        secret, body.code, user.last_accepted_totp_counter
    )
    if not verified:
        challenge.failed_attempts += 1
        if challenge.failed_attempts >= 5:
            challenge.consumed_at = _utcnow()
        await session.commit()
        return endpoint_problem(
            request,
            400,
            "Invalid code.",
            "The 6-digit verification code is invalid or has expired.",
        )
    # Verification successful: record counter, update last login, consume challenge
    user.last_accepted_totp_counter = accepted_counter
    user.last_login_at = _utcnow()
    challenge.consumed_at = _utcnow()
    await session.flush()
    await SessionService(session).start_session(user, body.remember_me, request, response)
    await session.commit()
    return _user_dto(user)


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    await SessionService(session).sign_out(
        request, response, current.user_id, current.session_id
    )
    await session.commit()
    return {"message": "Logged out successfully."}


@router.get("/me", response_model=UserDto)
async def get_current_user(
    request: Request,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    if current.user_id is None:
        return endpoint_problem(
            request, 401, "Unauthenticated.", "You are not authenticated."
        )
    user = (
        await session.execute(select(AppUser).where(AppUser.id == current.user_id))
    ).scalar_one_or_none()
    if user is None or user.status.lower() != "approved":
        return endpoint_problem(
            request, 401, "Unauthorized.", "User account is invalid or unapproved."
        )
    return _user_dto(user)


@router.post(
    "/refresh", response_model=UserDto, dependencies=[Depends(require_refresh_policy)]
)
async def refresh(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    result = await SessionService(session).refresh(request, response)
    if result.outcome != RefreshOutcome.REFRESHED or result.user is None:
        detail = {
            RefreshOutcome.MISSING: "No active session. Please sign in.",
            RefreshOutcome.EXPIRED: "Your session has expired. Please sign in again.",
            RefreshOutcome.REUSE_DETECTED: "This session was signed out for security. Please sign in again.",
            RefreshOutcome.USER_INACTIVE: "Your account is no longer active.",
        }.get(result.outcome, "Your session is no longer valid. Please sign in again.")
        await session.commit()
        return endpoint_problem(request, 401, "Session ended.", detail)
    await session.commit()
    return _user_dto(result.user)


@router.get("/sessions", dependencies=[Depends(require_user)])
async def list_sessions(
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    if current.user_id is None:
        return Response(status_code=401)
    return await SessionService(session).list_active(current.user_id, current.session_id)


@router.delete("/sessions/{session_id:uuid}", dependencies=[Depends(require_user)])
async def revoke_session(
    session_id: UUID,
    request: Request,
    response: Response,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    if current.user_id is None:
        return Response(status_code=401)
    service = SessionService(session)
    revoked = await service.revoke(session_id, current.user_id, "RevokedByUser")
    if not revoked:
        return endpoint_problem(
            request,
            404,
            "Session not found.",
            "No session with that id belongs to your account.",
        )
    if session_id == current.session_id:
        service.clear_cookies(request, response)
    await session.commit()
    return Response(status_code=204)


@router.post("/logout-all", dependencies=[Depends(require_user)])
async def logout_all(
    request: Request,
    response: Response,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    if current.user_id is None:
        return Response(status_code=401)
    service = SessionService(session)
    count = await service.revoke_all(current.user_id, None, "LogoutAll")
    service.clear_cookies(request, response)
    await session.commit()
    return {"message": "Signed out of all devices.", "revokedSessions": count}


def _bad_challenge(request: Request):
    return endpoint_problem(
        request,
        400,
        "Invalid or expired MFA challenge.",
        "The MFA challenge is invalid, expired, or has already been used. Please log in again.",
    )
