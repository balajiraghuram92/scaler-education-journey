"""Ported from api/Models/ChatConversation.cs."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .app_user import AppUser
    from .chat_message import ChatMessage
    from .lesson import Lesson


class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    __table_args__ = (
        Index("ix_chat_conversations_user_id", "user_id"),
        Index("ix_chat_conversations_lesson_id", "lesson_id"),
        Index("ix_chat_conversations_updated_at", "updated_at"),
    )

    id: Mapped[UUID] = mapped_column("id", Uuid, primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(ForeignKey("app_users.id", ondelete="CASCADE"))
    lesson_id: Mapped[int | None] = mapped_column(
        ForeignKey("lessons.id", ondelete="SET NULL")
    )
    title: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped[AppUser | None] = relationship("AppUser", lazy="raise")
    lesson: Mapped[Lesson | None] = relationship("Lesson", lazy="raise")
    messages: Mapped[list[ChatMessage]] = relationship(
        "ChatMessage", back_populates="conversation", lazy="raise"
    )
