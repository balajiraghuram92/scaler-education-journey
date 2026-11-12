"""Ported from api/Endpoints/AdminEndpoints.cs."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..errors import endpoint_problem
from ..models.app_user import AppUser
from ..models.chat_message import ChatMessage
from ..models.mfa_challenge import MfaChallenge
from ..schemas.auth_dtos import RejectUserRequest, UserDto
from ..schemas.chat_dtos import UserUsageDto
from ..services.auth.current_user import (
    CurrentUser,
    get_current_user_optional,
    require_admin,
)
from ..services.budget_guard_service import BudgetGuardService
from ..services.email.smtp_email_notification_service import (
    SmtpEmailNotificationService,
)
from ..settings import get_settings

router = APIRouter(prefix="/api/admin", tags=["admin"])


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


async def _load_approved_admin(
    session: AsyncSession, current: CurrentUser
) -> AppUser | None:
    if current.user_id is None:
        return None
    admin = (
        await session.execute(select(AppUser).where(AppUser.id == current.user_id))
    ).scalar_one_or_none()
    if admin is None or admin.role != "Admin" or admin.status != "Approved":
        return None
    return admin


@router.get("/users", dependencies=[Depends(require_admin)])
async def get_all_users(
    request: Request,
    status: str | None = None,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    admin = await _load_approved_admin(session, current)
    if admin is None:
        return endpoint_problem(
            request, 403, "Forbidden", "Administrative privileges required."
        )
    stmt = select(AppUser)
    if status and status.strip() and status.strip().lower() != "all":
        stmt = stmt.where(AppUser.status == status)
    stmt = stmt.order_by(desc(AppUser.created_at))
    users = (await session.execute(stmt)).scalars().all()
    return [_user_dto(u) for u in users]


@router.post("/users/{user_id:int}/approve", dependencies=[Depends(require_admin)])
async def approve_user(
    user_id: int,
    background: BackgroundTasks,
    request: Request,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    admin = await _load_approved_admin(session, current)
    if admin is None:
        return endpoint_problem(
            request, 403, "Forbidden", "Administrative privileges required."
        )
    user = (
        await session.execute(select(AppUser).where(AppUser.id == user_id))
    ).scalar_one_or_none()
    if user is None:
        return endpoint_problem(
            request, 404, "User not found.", f"No user found with ID {user_id}."
        )
    user.status = "Approved"
    user.decided_at = datetime.now(UTC)
    user.decided_by_user_id = admin.id
    await session.commit()
    background.add_task(_email_service().send_user_approved_notice, user)
    return _user_dto(user)


@router.post("/users/{user_id:int}/reject", dependencies=[Depends(require_admin)])
async def reject_user(
    user_id: int,
    request: Request,
    background: BackgroundTasks,
    body: RejectUserRequest | None = None,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    admin = await _load_approved_admin(session, current)
    if admin is None:
        return endpoint_problem(
            request, 403, "Forbidden", "Administrative privileges required."
        )
    user = (
        await session.execute(select(AppUser).where(AppUser.id == user_id))
    ).scalar_one_or_none()
    if user is None:
        return endpoint_problem(
            request, 404, "User not found.", f"No user found with ID {user_id}."
        )
    user.status = "Rejected"
    user.decided_at = datetime.now(UTC)
    user.decided_by_user_id = admin.id
    await session.commit()
    reason = body.reason if body else None
    background.add_task(_email_service().send_user_rejected_notice, user, reason)
    return _user_dto(user)


# Emergency self-recovery if the sole admin loses their TOTP device:
# Run directly in PostgreSQL:
# UPDATE app_users SET totp_enabled = false, totp_secret_encrypted = null, last_accepted_totp_counter = null WHERE email = 'admin@neuralascent.local';
@router.post("/users/{user_id:int}/reset-totp", dependencies=[Depends(require_admin)])
async def reset_totp(
    user_id: int,
    request: Request,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    admin = await _load_approved_admin(session, current)
    if admin is None:
        return endpoint_problem(
            request, 403, "Forbidden", "Administrative privileges required."
        )
    user = (
        await session.execute(select(AppUser).where(AppUser.id == user_id))
    ).scalar_one_or_none()
    if user is None:
        return endpoint_problem(
            request, 404, "User not found.", f"No user found with ID {user_id}."
        )
    now = datetime.now(UTC)
    user.totp_enabled = False
    user.totp_secret_encrypted = None
    user.last_accepted_totp_counter = None
    challenges = (
        await session.execute(
            select(MfaChallenge).where(
                MfaChallenge.user_id == user_id, MfaChallenge.consumed_at.is_(None)
            )
        )
    ).scalars().all()
    for challenge in challenges:
        challenge.consumed_at = now
    await session.commit()
    return {
        "message": f"TOTP second-factor reset successfully for user {user.email}. The user will be required to re-enroll on their next login.",
        "userId": user.id,
        "email": user.email,
        "totpEnabled": False,
    }


@router.get("/usage/today", dependencies=[Depends(require_admin)])
async def get_usage_today(
    request: Request,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    admin = await _load_approved_admin(session, current)
    if admin is None:
        return endpoint_problem(
            request, 403, "Forbidden", "Administrative privileges required."
        )
    return await BudgetGuardService(session).get_today_usage()


@router.get("/usage/by-user", dependencies=[Depends(require_admin)])
async def get_usage_by_user(
    request: Request,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    admin = await _load_approved_admin(session, current)
    if admin is None:
        return endpoint_problem(
            request, 403, "Forbidden", "Administrative privileges required."
        )
    from ..models.chat_conversation import ChatConversation

    stmt = (
        select(
            ChatConversation.user_id,
            AppUser.email,
            AppUser.display_name,
            func.count(ChatMessage.id),
            func.coalesce(func.sum(ChatMessage.estimated_cost_usd), 0),
            func.coalesce(func.sum(ChatMessage.prompt_tokens), 0),
            func.coalesce(func.sum(ChatMessage.completion_tokens), 0),
            func.max(ChatMessage.created_at),
        )
        .select_from(ChatMessage)
        .join(ChatConversation, ChatMessage.conversation_id == ChatConversation.id)
        .join(AppUser, ChatConversation.user_id == AppUser.id)
        .where(ChatMessage.role == "assistant")
        .group_by(ChatConversation.user_id, AppUser.email, AppUser.display_name)
        .order_by(desc(func.coalesce(func.sum(ChatMessage.estimated_cost_usd), 0)))
    )
    rows = (await session.execute(stmt)).all()
    return [
        UserUsageDto(
            user_id=row[0],
            email=row[1],
            display_name=row[2],
            total_requests=row[3],
            total_cost_usd=Decimal(row[4] if row[4] is not None else 0).quantize(
                Decimal("0.000001")
            ),
            total_prompt_tokens=row[5],
            total_completion_tokens=row[6],
            last_request_at=row[7],
        )
        for row in rows
    ]
