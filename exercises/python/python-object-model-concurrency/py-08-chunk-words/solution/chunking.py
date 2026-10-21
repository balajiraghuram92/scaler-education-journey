from __future__ import annotations

from collections.abc import Iterable, Iterator


def chunk_words(lines: Iterable[str], size: int, overlap: int = 0) -> Iterator[str]:
    """Lazily yield chunks of `size` words, repeating the last `overlap` words."""
    if size < 1:
        raise ValueError("size must be >= 1")
    if not 0 <= overlap < size:
        raise ValueError("overlap must satisfy 0 <= overlap < size")
    return _chunks(lines, size, overlap)


def _chunks(lines: Iterable[str], size: int, overlap: int) -> Iterator[str]:
    buf: list[str] = []
    fresh = 0  # words added since the last yielded chunk
    for line in lines:
        for word in line.split():
            buf.append(word)
            fresh += 1
            if len(buf) == size:
                yield " ".join(buf)
                buf = buf[size - overlap:]
                fresh = 0
    if fresh:
        yield " ".join(buf)
