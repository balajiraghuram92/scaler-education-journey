"""Ported from api/Models/AuthDtos.cs.

Request models mirror C# binding semantics: ASP.NET does not validate
[Required] on minimal-API bodies, so a missing reference-type property binds
as null and the handler decides. Hence request fields default to None and
handlers keep the C# outcome (400 problem, not 422).
"""

from __future__ import annotations

from uuid import UUID

from .base import CamelModel, DotNetDateTime


class SignupRequest(CamelModel):
    email: str | None = None
    password: str | None = None
    display_name: str | None = None


class LoginRequest(CamelModel):
    email: str | None = None
    password: str | None = None


class LoginResponse(CamelModel):
    challenge_id: UUID
    requires_enrollment: bool


class TotpEnrollStartRequest(CamelModel):
    challenge_id: UUID | None = None


class TotpEnrollStartResponse(CamelModel):
    otp_auth_uri: str
    manual_entry_code: str


class TotpEnrollConfirmRequest(CamelModel):
    challenge_id: UUID | None = None
    code: str | None = None
    remember_me: bool = False


class TotpVerifyRequest(CamelModel):
    challenge_id: UUID | None = None
    code: str | None = None
    remember_me: bool = False


class RejectUserRequest(CamelModel):
    reason: str | None = None


class UserDto(CamelModel):
    id: int
    email: str
    display_name: str | None
    role: str
    status: str
    created_at: DotNetDateTime
    last_login_at: DotNetDateTime | None = None
