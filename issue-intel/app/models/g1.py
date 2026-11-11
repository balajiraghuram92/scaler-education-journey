"""G1 ORM models: knowledge foundation tables."""
from __future__ import annotations

import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.gateway import ModelCall  # noqa: F401  (register table)


class Acl(Base):
    __tablename__ = "acls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    modules: Mapped[str] = mapped_column(Text)
    departments: Mapped[str] = mapped_column(Text)
    restriction: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(Text)


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    handle: Mapped[str] = mapped_column(Text, unique=True)
    name: Mapped[str] = mapped_column(Text)
    team: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(Text, unique=True)
    display_name: Mapped[str] = mapped_column(Text)


class Entitlement(Base):
    __tablename__ = "entitlements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    modules: Mapped[str] = mapped_column(Text)
    departments: Mapped[str] = mapped_column(Text)
    max_restriction: Mapped[int] = mapped_column(Integer)


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(Text)
    source_key: Mapped[str] = mapped_column(Text)
    module: Mapped[str] = mapped_column(Text)
    filed_module: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    body: Mapped[str] = mapped_column(Text)
    version: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    raw_resolution: Mapped[str] = mapped_column(Text, default="")
    outcome: Mapped[str] = mapped_column(Text, default="UNKNOWN")
    fixed_change: Mapped[str] = mapped_column(Text, default="")
    customer_ref: Mapped[str] = mapped_column(Text, default="")
    acl_id: Mapped[int] = mapped_column(ForeignKey("acls.id"))


class Thread(Base):
    __tablename__ = "threads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(Text, unique=True)
    case_source: Mapped[str] = mapped_column(Text)
    case_key: Mapped[str] = mapped_column(Text)
    acl_id: Mapped[int] = mapped_column(ForeignKey("acls.id"))


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("threads.id"))
    seq: Mapped[int] = mapped_column(Integer)
    author: Mapped[str] = mapped_column(Text)
    text: Mapped[str] = mapped_column(Text)
    acl_id: Mapped[int] = mapped_column(ForeignKey("acls.id"))


class Change(Base):
    __tablename__ = "changes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ref: Mapped[str] = mapped_column(Text, unique=True)
    repo: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(Text)
    reviewers: Mapped[str] = mapped_column(Text, default="")
    files: Mapped[str] = mapped_column(Text, default="")
    message: Mapped[str] = mapped_column(Text, default="")
    merged_at: Mapped[datetime.datetime | None] = mapped_column(DateTime(timezone=True))
    legacy_id: Mapped[str] = mapped_column(Text, default="")
    planned_seq: Mapped[int | None] = mapped_column(Integer)
    acl_id: Mapped[int] = mapped_column(ForeignKey("acls.id"))


class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_type: Mapped[str] = mapped_column(Text)
    owner_key: Mapped[str] = mapped_column(Text)
    seq: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[Any] = mapped_column(Vector(64))
    tsv: Mapped[Any] = mapped_column(TSVECTOR)
    acl_id: Mapped[int] = mapped_column(ForeignKey("acls.id"))


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_type: Mapped[str] = mapped_column(Text)
    from_key: Mapped[str] = mapped_column(Text)
    to_type: Mapped[str] = mapped_column(Text)
    to_key: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(Text)
    evidence: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)


class Ownership(Base):
    __tablename__ = "ownership"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    scope: Mapped[str] = mapped_column(Text)
    target: Mapped[str] = mapped_column(Text)
    owner_handle: Mapped[str] = mapped_column(Text)


class EvalCase(Base):
    __tablename__ = "eval_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(Text)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB)
    expected: Mapped[dict[str, Any]] = mapped_column(JSONB)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )
