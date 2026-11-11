"""Citation check: every cited evidence id must have been retrieved. Pure."""
from __future__ import annotations

import re
from dataclasses import dataclass

CITE_RE = re.compile(r"\[(E\d+)\]")


@dataclass
class CitationReport:
    cited: list[str]
    unknown: list[str]
    ok: bool


def check_citations(answer_text: str, evidence_ids: list[str]) -> CitationReport:
    cited = CITE_RE.findall(answer_text)
    allowed = set(evidence_ids)
    unknown = sorted({c for c in cited if c not in allowed})
    return CitationReport(cited=cited, unknown=unknown, ok=not unknown)
