from __future__ import annotations

from collections.abc import Iterable, Iterator


def chunk_words(lines: Iterable[str], size: int, overlap: int = 0) -> Iterator[str]:
    """Lazily yield chunks of ``size`` words, repeating the last ``overlap`` words of the previous chunk.

    - words are whitespace-separated tokens from ``line.split()``; chunks span line boundaries
      and blank lines are ignored; each chunk is its words joined by single spaces
    - ``size < 1`` or ``overlap`` outside ``0 <= overlap < size`` raises ``ValueError`` from the
      call to ``chunk_words(...)`` itself, before any iteration (so this public function cannot
      itself be a generator function; have it return a private generator)
    - after a full chunk is yielded, the next chunk starts with the last ``overlap`` words of it
    - at the end, yield the final partial chunk only if it holds at least one word that has not
      been emitted yet (never a chunk made only of overlap words)
    - be lazy: pull from ``lines`` only as needed, work with generators, and allow closing early
    """
    raise NotImplementedError("Implement chunk_words")
