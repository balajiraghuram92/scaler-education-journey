"""Fake docs service: tiny static manual for the Tessera Editor."""
from __future__ import annotations

from dataclasses import dataclass

DOCS: dict[str, dict[str, str]] = {
    "VersionControl": {
        "title": "Commit trailers and branch policy",
        "text": (
            "Trailer lines use the FIRST colon as the separator; values may "
            "contain further colons. Branch names must not contain '..' "
            "anywhere. The merge base of two histories is their first common "
            "ancestor; walks include the root commit."
        ),
    },
    "Localization": {
        "title": "Plurals, fallback and casing",
        "text": (
            "French treats 0 as singular. Resource fallback order is exact "
            "culture, parent culture, then invariant. Culture-code "
            "normalisation and resource-key building always use invariant "
            "casing; current-culture casing breaks tr-TR lookups."
        ),
    },
    "UiState": {
        "title": "Recent files, layout and settings",
        "text": (
            "The recent-files list holds no duplicates; re-adding moves the "
            "entry to the front. Layout files store name, width, height in "
            "that order. Settings keys are case-sensitive; the theme key is "
            "'Theme'."
        ),
    },
    "AssetImport": {
        "title": "Mipmaps and normalisation",
        "text": (
            "Mipmap levels halve the size rounding down, minimum 1. Peak "
            "normalisation targets 0.99 full scale so peaks never clip."
        ),
    },
}


@dataclass
class DocHit:
    module: str
    title: str
    snippet: str
    score: float


def search_docs(query: str, limit: int = 3) -> list[DocHit]:
    words = {w.lower() for w in query.split() if len(w) > 2}
    hits = []
    for module, doc in DOCS.items():
        text = f"{doc['title']} {doc['text']}".lower()
        score = sum(1 for w in words if w in text)
        hits.append(DocHit(module, doc["title"], doc["text"][:400], float(score)))
    hits.sort(key=lambda h: h.score, reverse=True)
    return [h for h in hits if h.score > 0][:limit] or hits[:1]
