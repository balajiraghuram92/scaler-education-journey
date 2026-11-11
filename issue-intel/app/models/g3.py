"""G3 ORM models: fix candidates, attempts, PRs, checks, tokens, profiles."""
from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class FixCandidate(Base):
    __tablename__ = "fix_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"))
    ticket_key: Mapped[str] = mapped_column(Text)
    module: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    owner_opt_in: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(Text, default="PENDING")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )


class FixAttempt(Base):
    __tablename__ = "fix_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("fix_candidates.id"))
    attempt_no: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(Text, default="RUNNING")
    branch: Mapped[str] = mapped_column(Text, default="")
    trace: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    tokens_in: Mapped[int] = mapped_column(Integer, default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0)
    build_output: Mapped[str] = mapped_column(Text, default="")
    test_output: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )


class FixPr(Base):
    __tablename__ = "fix_prs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attempt_id: Mapped[int] = mapped_column(ForeignKey("fix_attempts.id"))
    kind: Mapped[str] = mapped_column(Text)
    branch: Mapped[str] = mapped_column(Text)
    base: Mapped[str] = mapped_column(Text, default="main")
    title: Mapped[str] = mapped_column(Text, default="")
    root_cause: Mapped[str] = mapped_column(Text, default="")
    citations: Mapped[list[str]] = mapped_column(JSONB, default=list)
    risk_note: Mapped[str] = mapped_column(Text, default="")
    test_results: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    diff: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(Text, default="OPEN")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )


class FinalCheck(Base):
    __tablename__ = "final_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("runs.id"))
    attempt_id: Mapped[int | None] = mapped_column(ForeignKey("fix_attempts.id"))
    verdict: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )


class ApprovalToken(Base):
    __tablename__ = "approval_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    token_hash: Mapped[str] = mapped_column(Text, unique=True)
    run_id: Mapped[str] = mapped_column(String(64))
    ticket_key: Mapped[str] = mapped_column(Text)
    payload_hash: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(Text)
    used: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.datetime.now(datetime.UTC)
    )


class AudienceProfile(Base):
    __tablename__ = "audience_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, unique=True)
    departments: Mapped[str] = mapped_column(Text)
    max_restriction: Mapped[int] = mapped_column(Integer)
    hide_fields: Mapped[list[str]] = mapped_column(JSONB, default=list)


class DeveloperProfile(Base):
    __tablename__ = "developer_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    handle: Mapped[str] = mapped_column(Text, unique=True)
    modules: Mapped[str] = mapped_column(Text)
    opt_in_fix: Mapped[bool] = mapped_column(Boolean, default=False)
