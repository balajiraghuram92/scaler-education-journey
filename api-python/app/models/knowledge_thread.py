"""Ported from api/Models/KnowledgeThread.cs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .knowledge_thread_step import KnowledgeThreadStep


class KnowledgeThread(Base):
    __tablename__ = "knowledge_threads"
    __table_args__ = (Index("IX_knowledge_threads_Domain", "Domain"),)

    id: Mapped[int] = mapped_column("Id", Integer, primary_key=True)
    domain: Mapped[str] = mapped_column("Domain", Text)
    raw_path: Mapped[str] = mapped_column("RawPath", Text)
    order_index: Mapped[int] = mapped_column("OrderIndex", Integer)

    steps: Mapped[list[KnowledgeThreadStep]] = relationship(
        "KnowledgeThreadStep", back_populates="thread", lazy="raise"
    )
