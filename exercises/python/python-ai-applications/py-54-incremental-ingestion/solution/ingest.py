from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Chunk:
    chunk_id: str
    doc_id: str
    index: int
    text: str
    start: int
    end: int
    content_hash: str


def chunk_words(doc_id: str, text: str, size: int = 120, overlap: int = 20) -> list[Chunk]:
    if size <= 0 or not 0 <= overlap < size:
        raise ValueError("need size > 0 and 0 <= overlap < size")
    spans = [m.span() for m in re.finditer(r"\S+", text)]
    chunks: list[Chunk] = []
    for i, first in enumerate(range(0, len(spans), size - overlap)):
        window = spans[first:first + size]
        start, end = window[0][0], window[-1][1]
        body = text[start:end]
        digest = hashlib.sha256(body.encode()).hexdigest()
        chunks.append(Chunk(f"{doc_id}#{i}", doc_id, i, body, start, end, digest))
        if first + size >= len(spans):
            break
    return chunks


class Embedder(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class VectorStore:
    """In-memory stand-in for a vector database: chunk_id -> (content_hash, vector)."""

    def __init__(self) -> None:
        self._rows: dict[str, tuple[str, list[float]]] = {}

    def hash_of(self, chunk_id: str) -> str | None:
        row = self._rows.get(chunk_id)
        return row[0] if row else None

    def ids_for(self, doc_id: str) -> set[str]:
        prefix = f"{doc_id}#"
        return {cid for cid in self._rows if cid.startswith(prefix)}

    def upsert(self, chunk: Chunk, vector: list[float]) -> None:
        self._rows[chunk.chunk_id] = (chunk.content_hash, vector)

    def delete(self, chunk_ids: set[str]) -> None:
        for cid in chunk_ids:
            self._rows.pop(cid, None)

    def __len__(self) -> int:
        return len(self._rows)


@dataclass(frozen=True, slots=True)
class SyncReport:
    added: int
    updated: int
    unchanged: int
    deleted: int


class IndexSync:
    def __init__(self, embedder: Embedder, store: VectorStore, *, size: int = 120,
                 overlap: int = 20) -> None:
        self._embedder, self._store = embedder, store
        self._size, self._overlap = size, overlap

    async def sync(self, doc_id: str, text: str) -> SyncReport:
        chunks = chunk_words(doc_id, text, self._size, self._overlap)
        existing = self._store.ids_for(doc_id)
        todo = [c for c in chunks if self._store.hash_of(c.chunk_id) != c.content_hash]
        if todo:
            vectors = await self._embedder.embed([c.text for c in todo])
            for chunk, vec in zip(todo, vectors, strict=True):
                self._store.upsert(chunk, vec)
        stale = existing - {c.chunk_id for c in chunks}
        self._store.delete(stale)
        added = sum(1 for c in todo if c.chunk_id not in existing)
        return SyncReport(added=added, updated=len(todo) - added,
                          unchanged=len(chunks) - len(todo), deleted=len(stale))
