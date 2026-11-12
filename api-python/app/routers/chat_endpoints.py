"""Ported from api/Endpoints/ChatEndpoints.cs."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db import get_session
from ..errors import endpoint_problem
from ..models.app_user import AppUser
from ..models.chat_conversation import ChatConversation
from ..models.chat_message import ChatMessage
from ..models.lesson import Lesson
from ..models.lesson_note import LessonNote
from ..schemas.chat_dtos import (
    ChatConversationDto,
    ChatMessageDto,
    CreateChatConversationRequest,
    SendChatMessageRequest,
)
from ..services.auth.current_user import (
    CurrentUser,
    get_current_user_optional,
    require_user,
)
from ..services.budget_guard_service import BudgetGuardService
from ..services.llama_api_client import ChatPromptMessage, LlamaApiClient
from ..settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chat", tags=["chat"])


def _utcnow() -> datetime:
    return datetime.now(UTC)


async def _load_approved_user(
    session: AsyncSession, current: CurrentUser
) -> AppUser | None:
    if current.user_id is None:
        return None
    user = (
        await session.execute(select(AppUser).where(AppUser.id == current.user_id))
    ).scalar_one_or_none()
    if user is None or user.status.lower() != "approved":
        return None
    return user


def _conversation_dto(conversation: ChatConversation) -> ChatConversationDto:
    return ChatConversationDto(
        id=conversation.id,
        user_id=conversation.user_id,
        lesson_id=conversation.lesson_id,
        title=conversation.title,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


def _message_dto(message: ChatMessage) -> ChatMessageDto:
    return ChatMessageDto(
        id=message.id,
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
        client_request_id=message.client_request_id,
        prompt_tokens=message.prompt_tokens,
        completion_tokens=message.completion_tokens,
        usage_estimated=message.usage_estimated,
        estimated_cost_usd=message.estimated_cost_usd,
        latency_ms=message.latency_ms,
        created_at=message.created_at,
    )


@router.post("/conversations", dependencies=[Depends(require_user)])
async def create_conversation(
    body: CreateChatConversationRequest,
    request: Request,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    user = await _load_approved_user(session, current)
    if user is None:
        return endpoint_problem(
            request,
            401,
            "Unauthorized",
            "User account is not approved or authenticated.",
        )
    title = body.title.strip() if body.title else None
    if body.lesson_id is not None:
        lesson = (
            await session.execute(select(Lesson).where(Lesson.id == body.lesson_id))
        ).scalar_one_or_none()
        if lesson is None:
            return endpoint_problem(
                request,
                404,
                "Lesson not found",
                f"No lesson found with ID {body.lesson_id}.",
            )
        if not title:
            title = f"Chat: {lesson.title}"
    if not title:
        title = "New Conversation"
    now = _utcnow()
    conversation = ChatConversation(
        user_id=user.id,
        lesson_id=body.lesson_id,
        title=title[:200] if len(title) > 200 else title,
        created_at=now,
        updated_at=now,
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return JSONResponse(
        status_code=201,
        headers={"Location": f"/api/chat/conversations/{conversation.id}"},
        content=_conversation_dto(conversation).model_dump(by_alias=True, mode="json"),
    )


@router.post("/conversations/{conversation_id:uuid}/messages", dependencies=[Depends(require_user)])
async def send_message(
    conversation_id: UUID,
    body: SendChatMessageRequest,
    request: Request,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    user = await _load_approved_user(session, current)
    if user is None:
        return endpoint_problem(
            request,
            401,
            "Unauthorized",
            "User account is not approved or authenticated.",
        )
    if not body.content or not body.content.strip():
        return endpoint_problem(
            request, 400, "Bad Request", "Message content cannot be empty."
        )
    conversation = (
        await session.execute(
            select(ChatConversation)
            .options(selectinload(ChatConversation.lesson))
            .where(
                ChatConversation.id == conversation_id,
                ChatConversation.user_id == user.id,
            )
        )
    ).scalar_one_or_none()
    if conversation is None:
        return endpoint_problem(
            request,
            404,
            "Conversation not found",
            f"Conversation {conversation_id} was not found.",
        )

    # Idempotency check: if clientRequestId already processed and responded to
    if body.client_request_id and body.client_request_id.strip():
        existing_user_msg = (
            await session.execute(
                select(ChatMessage).where(
                    ChatMessage.conversation_id == conversation_id,
                    ChatMessage.client_request_id == body.client_request_id,
                )
            )
        ).scalar_one_or_none()
        if existing_user_msg is not None:
            existing_assistant_msg = (
                await session.execute(
                    select(ChatMessage)
                    .where(
                        ChatMessage.conversation_id == conversation_id,
                        ChatMessage.role == "assistant",
                        ChatMessage.created_at >= existing_user_msg.created_at,
                    )
                    .order_by(ChatMessage.created_at)
                )
            ).scalars().first()
            if existing_assistant_msg is not None:
                return _message_dto(existing_assistant_msg)

    # Budget Guard Check before calling model
    allowed, usage = await BudgetGuardService(session).try_reserve_request()
    if not allowed:
        return endpoint_problem(
            request,
            429,
            "Daily AI Compute Cap Reached",
            f"Neuralascent's shared daily AI budget of ${float(usage.daily_cap_usd):.2f}/day has been reached for today (UTC). The cap resets at midnight UTC. Please try again tomorrow.",
        )

    # Save User Message
    user_msg = ChatMessage(
        conversation_id=conversation_id,
        role="user",
        content=body.content.strip(),
        client_request_id=body.client_request_id.strip()
        if body.client_request_id
        else None,
        usage_estimated=False,
        created_at=_utcnow(),
    )
    session.add(user_msg)
    # Committed before the LLM call, as in C#: the user message persists even if
    # the completion fails.
    await session.commit()

    # Build prompt context
    llama_options = get_settings().llama_api
    max_context_chars = (
        llama_options.max_context_characters
        if llama_options.max_context_characters > 0
        else 6000
    )
    max_history = (
        llama_options.max_history_messages
        if llama_options.max_history_messages > 0
        else 10
    )

    # Prompt strings copied verbatim from ChatEndpoints.cs; do not rewrite.
    lines = [
        "You are the Neuralascent AI Learning Assistant, dedicated to helping the learner understand computer science, distributed systems, and software engineering concepts."
    ]
    if conversation.lesson is not None:
        lines.append("")
        lines.append("--- CURRENT LESSON MATERIAL ---")
        lines.append(f"Title: {conversation.lesson.title}")
        if conversation.lesson.description and conversation.lesson.description.strip():
            lines.append(f"Overview: {conversation.lesson.description}")
        # Fetch any lesson notes for additional grounding
        lesson_notes = (
            await session.execute(
                select(LessonNote.content_body)
                .where(LessonNote.lesson_id == conversation.lesson.id)
                .order_by(LessonNote.order_index)
                .limit(5)
            )
        ).scalars().all()
        if lesson_notes:
            lines.append("Key Notes:")
            for note in lesson_notes:
                lines.append(f"- {note}")
        lines.append("--- END OF LESSON MATERIAL ---")
        lines.append(
            "Ground your responses in this lesson material whenever applicable. Be educational, encouraging, and clear."
        )
    system_prompt = "\n".join(lines) + "\n"
    if len(system_prompt) > max_context_chars:
        system_prompt = system_prompt[:max_context_chars] + "\n[Context Truncated]"

    # Retrieve conversation history (excluding the user message we just added)
    history_rows = (
        await session.execute(
            select(ChatMessage)
            .where(
                ChatMessage.conversation_id == conversation_id,
                ChatMessage.id != user_msg.id,
                ChatMessage.role.in_(["user", "assistant"]),
            )
            .order_by(ChatMessage.created_at.desc())
            .limit(max_history)
        )
    ).scalars().all()
    history_rows = sorted(history_rows, key=lambda m: m.created_at)

    prompt_messages = [ChatPromptMessage(role="system", content=system_prompt)]
    for history_msg in history_rows:
        prompt_messages.append(
            ChatPromptMessage(role=history_msg.role, content=history_msg.content)
        )
    prompt_messages.append(ChatPromptMessage(role="user", content=user_msg.content))

    # Call Meta Llama API
    try:
        reply = await LlamaApiClient().generate_completion(prompt_messages)
    except Exception as exc:
        logger.error(
            "Failed to get completion from Llama API for conversation %s: %s",
            conversation_id,
            exc,
        )
        return endpoint_problem(
            request,
            502,
            "AI Service Error",
            "Failed to communicate with the AI language service. Please try again in a few moments.",
        )

    # Save Assistant Message
    assistant_msg = ChatMessage(
        conversation_id=conversation_id,
        role="assistant",
        content=reply.reply_content,
        prompt_tokens=reply.prompt_tokens,
        completion_tokens=reply.completion_tokens,
        usage_estimated=reply.usage_estimated,
        estimated_cost_usd=reply.estimated_cost_usd,
        latency_ms=reply.latency_ms,
        created_at=_utcnow(),
    )
    conversation.updated_at = _utcnow()
    session.add(assistant_msg)
    await session.commit()
    return _message_dto(assistant_msg)


@router.get(
    "/conversations/{conversation_id:uuid}/messages", dependencies=[Depends(require_user)]
)
async def get_messages(
    conversation_id: UUID,
    request: Request,
    current: CurrentUser = Depends(get_current_user_optional),
    session: AsyncSession = Depends(get_session),
):
    user = await _load_approved_user(session, current)
    if user is None:
        return endpoint_problem(
            request,
            401,
            "Unauthorized",
            "User account is not approved or authenticated.",
        )
    conversation = (
        await session.execute(
            select(ChatConversation).where(
                ChatConversation.id == conversation_id,
                ChatConversation.user_id == user.id,
            )
        )
    ).scalar_one_or_none()
    if conversation is None:
        return endpoint_problem(
            request,
            404,
            "Conversation not found",
            f"Conversation {conversation_id} was not found.",
        )
    messages = (
        await session.execute(
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at)
        )
    ).scalars().all()
    return [_message_dto(m) for m in messages]
