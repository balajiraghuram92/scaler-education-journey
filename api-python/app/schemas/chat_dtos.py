"""Ported from api/Models/ChatDtos.cs."""

from __future__ import annotations

from uuid import UUID

from .base import CamelModel, DotNetDateTime, DotNetDecimal


class CreateChatConversationRequest(CamelModel):
    lesson_id: int | None = None
    title: str | None = None


class ChatConversationDto(CamelModel):
    id: UUID
    user_id: int
    lesson_id: int | None
    title: str | None
    created_at: DotNetDateTime
    updated_at: DotNetDateTime


class SendChatMessageRequest(CamelModel):
    content: str | None = None
    client_request_id: str | None = None


class ChatMessageDto(CamelModel):
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    client_request_id: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    usage_estimated: bool
    estimated_cost_usd: DotNetDecimal | None
    latency_ms: int | None
    created_at: DotNetDateTime


class UsageSummaryDto(CamelModel):
    total_cost_today_usd: DotNetDecimal
    daily_cap_usd: DotNetDecimal
    request_count_today: int
    max_daily_requests: int
    budget_exceeded: bool


class UserUsageDto(CamelModel):
    user_id: int
    email: str
    display_name: str | None
    total_requests: int
    total_cost_usd: DotNetDecimal
    total_prompt_tokens: int
    total_completion_tokens: int
    last_request_at: DotNetDateTime | None
