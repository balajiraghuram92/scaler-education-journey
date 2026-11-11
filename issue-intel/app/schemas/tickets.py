"""Schemas for the ticket similarity endpoint."""
from __future__ import annotations

from pydantic import BaseModel


class EvidenceItem(BaseModel):
    id: str
    kind: str
    key: str
    title: str
    snippet: str
    outcome: str = ""


class Claim(BaseModel):
    text: str
    cites: list[str]


class LineageItem(BaseModel):
    key: str
    outcome: str
    duplicates: list[str]
    fixed_by: list[str]
    owner: str | None


class SimilarResponse(BaseModel):
    ticket: str
    evidence: list[EvidenceItem]
    claims: list[Claim]
    lineage: list[LineageItem]
    answer_text: str
