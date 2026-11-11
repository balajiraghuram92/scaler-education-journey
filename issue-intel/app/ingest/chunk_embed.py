"""Chunk owner text and embed it. Idempotent by (owner_type, owner_key, seq)."""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.gateway.gateway import ModelGateway
from app.models.g1 import Case, Change, Chunk, Message, Thread

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    if not words:
        return []
    chunks = []
    start = 0
    while start < len(words):
        chunks.append(" ".join(words[start : start + size]))
        if start + size >= len(words):
            break
        start += size - overlap
    return chunks


async def _chunked_keys(session: AsyncSession, owner_type: str) -> set[tuple[str, int]]:
    rows = (
        await session.execute(
            select(Chunk.owner_key, Chunk.seq).where(Chunk.owner_type == owner_type)
        )
    ).all()
    return {(key, seq) for key, seq in rows}


async def _store_chunks(
    session: AsyncSession, gateway: ModelGateway, owner_type: str, owner_key: str,
    text: str, acl_id: int, have: set[tuple[str, int]], run_id: str | None,
) -> int:
    pieces = chunk_text(text)
    missing = [(seq, piece) for seq, piece in enumerate(pieces) if (owner_key, seq) not in have]
    if not missing:
        return 0
    vectors = await gateway.embed([piece for _, piece in missing], run_id=run_id)
    for (seq, piece), vector in zip(missing, vectors, strict=True):
        session.add(
            Chunk(owner_type=owner_type, owner_key=owner_key, seq=seq, text=piece,
                  embedding=vector,
                  tsv=func.to_tsvector("english", piece), acl_id=acl_id)
        )
        have.add((owner_key, seq))
    await session.flush()
    return len(missing)


async def chunk_and_embed(
    session: AsyncSession, gateway: ModelGateway, run_id: str | None = None
) -> int:
    total = 0
    have_case = await _chunked_keys(session, "case")
    for case in (await session.execute(select(Case))).scalars().all():
        total += await _store_chunks(
            session, gateway, "case", case.source_key,
            f"{case.title}\n{case.body}\n{case.raw_resolution}",
            case.acl_id, have_case, run_id,
        )
    have_thread = await _chunked_keys(session, "thread")
    threads = {t.id: t for t in (await session.execute(select(Thread))).scalars().all()}
    messages: dict[int, list[str]] = {}
    for row in (await session.execute(select(Message).order_by(Message.seq))).scalars().all():
        messages.setdefault(row.thread_id, []).append(f"{row.author}: {row.text}")
    for thread_id, lines in messages.items():
        thread = threads[thread_id]
        total += await _store_chunks(
            session, gateway, "thread", thread.key, "\n".join(lines),
            thread.acl_id, have_thread, run_id,
        )
    have_change = await _chunked_keys(session, "change")
    for change in (await session.execute(select(Change))).scalars().all():
        total += await _store_chunks(
            session, gateway, "change", change.ref,
            f"{change.message}\nFiles: {change.files}", change.acl_id,
            have_change, run_id,
        )
    return total
