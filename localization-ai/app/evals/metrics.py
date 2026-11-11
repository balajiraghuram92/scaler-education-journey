"""Deterministic metric functions. Pure: no I/O, no model calls.

Glossary matching is case-sensitive substring matching: approved terms such
as "HUD" or "Links abbiegen" must appear exactly as approved.
"""

import re
from collections.abc import Sequence

_PLACEHOLDER_RE = re.compile(r"\{[^{}]*\}")


def extract_placeholders(text: str | None) -> list[str]:
    """Return every ``{...}`` token in source order (``{count}``, ``{speed}``)."""
    return _PLACEHOLDER_RE.findall(text or "")


def placeholder_preserved_ok(source: str | None, output: str | None) -> bool | None:
    """True when the output carries exactly the source's placeholders.

    None when the source has no placeholders: the case is excluded from the
    placeholder-preservation rate rather than counted as a pass.
    """
    expected = extract_placeholders(source)
    if not expected:
        return None
    return sorted(expected) == sorted(extract_placeholders(output))


def applicable_glossary_terms(source: str | None, terms: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Terms whose source side actually occurs in the source text."""
    haystack = source or ""
    return [(src, tgt) for src, tgt in terms if src and src in haystack]


def glossary_adherence_ok(source: str | None, output: str | None, terms: list[tuple[str, str]]) -> bool | None:
    """True when every applicable approved target term appears in the output.

    None when no glossary term applies to the source: the case is excluded
    from the adherence rate rather than counted as a pass.
    """
    applicable = applicable_glossary_terms(source, terms)
    if not applicable:
        return None
    haystack = output or ""
    return all(tgt and tgt in haystack for _, tgt in applicable)


def exact_match(output: str | None, gold: str | None) -> bool:
    """Byte-identical output and gold translation."""
    return (output or "") == (gold or "")


def _normalize(text: str | None) -> str:
    return " ".join((text or "").casefold().split())


def normalized_match(output: str | None, gold: str | None) -> bool:
    """Equal after casefolding and collapsing whitespace."""
    return _normalize(output) == _normalize(gold)


def rate(flags: Sequence[bool | None]) -> float | None:
    """Share of True over non-None flags; None when no case decided."""
    decided = [f for f in flags if f is not None]
    if not decided:
        return None
    return sum(decided) / len(decided)


def mean(values: Sequence[int | float | None]) -> float | None:
    """Mean over non-None values; None when every value is None."""
    present = [v for v in values if v is not None]
    if not present:
        return None
    return sum(present) / len(present)


def total(values: Sequence[int | float | None]) -> float:
    """Sum treating None as zero."""
    return float(sum(v or 0 for v in values))
