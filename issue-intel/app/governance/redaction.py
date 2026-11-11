"""Redaction: second line of defence after RLS. Pure functions."""
from __future__ import annotations

import re

from app.governance.entitlements import Entitlements

CUSTOMER_RE = re.compile(r"CUST-\d+")
EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def redact(text: str, ent: Entitlements) -> str:
    """Mask customer references and emails for viewers outside SE."""
    if "SE" in ent.departments:
        return text
    text = CUSTOMER_RE.sub("CUST-****", text)
    return EMAIL_RE.sub("***@***", text)
