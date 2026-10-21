from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Chunk:
    chunk_id: str  # f"{doc_id}#{index}"
    doc_id: str
    index: int
    text: str
    start: int  # character offsets: text[start:end] == chunk.text
    end: int
    content_hash: str  # SHA-256 hex digest of the chunk text


def chunk_words(doc_id: str, text: str, size: int = 120, overlap: int = 20) -> list[Chunk]:
    """Split ``text`` into word windows of ``size`` words advancing by ``size - overlap``.

    - stop once a window reaches the last word (no redundant trailing window)
    - ``text[chunk.start:chunk.end] == chunk.text``; ids are ``doc_id#0``, ``doc_id#1``, ...
    - ``content_hash`` is the SHA-256 hex digest of the chunk text
    - raise ``ValueError`` unless ``size > 0`` and ``0 <= overlap < size``
    - empty or whitespace-only text yields ``[]``
    """
    raise NotImplementedError("Implement chunk_words")


class Embedder(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class VectorStore:
    """In-memory stand-in for a vector database: chunk_id -> (content_hash, vector)."""

    def __init__(self) -> None:
        self._rows: dict[str, tuple[str, list[float]]] = {}

    def hash_of(self, chunk_id: str) -> str | None:
        """Stored content hash, or ``None`` when the chunk is not stored."""
        raise NotImplementedError("Implement VectorStore.hash_of")

    def ids_for(self, doc_id: str) -> set[str]:
        """All stored chunk ids of ``doc_id`` (document ``a`` must not match document ``ab``)."""
        raise NotImplementedError("Implement VectorStore.ids_for")

    def upsert(self, chunk: Chunk, vector: list[float]) -> None:
        raise NotImplementedError("Implement VectorStore.upsert")

    def delete(self, chunk_ids: set[str]) -> None:
        """Delete the given ids; unknown ids are ignored."""
        raise NotImplementedError("Implement VectorStore.delete")

    def __len__(self) -> int:
        raise NotImplementedError("Implement VectorStore.__len__")


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
        """Bring the store in line with ``text`` without re-embedding unchanged chunks.

        - embed only chunks whose stored hash is missing or different, in ONE batched call
        - upsert them; delete stored ids of this document that are not in the new chunk set
        - an unchanged document makes zero embedder calls
        - ``added``: new ids, ``updated``: existing ids with a new hash, ``unchanged``, ``deleted``
        """
        raise NotImplementedError("Implement IndexSync.sync")
