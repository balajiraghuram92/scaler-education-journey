"""Ported from api/Services/Reconciliation/NormalizationHelper.cs."""

from __future__ import annotations

import hashlib
import re


def normalize_text(text: str | None) -> str:
    if not text or not text.strip():
        return ""
    normalized = text.strip().lower()
    normalized = re.sub(r"\s+", " ", normalized)
    # Strip common punctuation differences
    normalized = re.sub(r"[^\w\s-]", "", normalized)
    return normalized.strip()


def generate_slug(text: str) -> str:
    if not text or not text.strip():
        return ""
    slug = text.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def compute_sha256_checksum(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
