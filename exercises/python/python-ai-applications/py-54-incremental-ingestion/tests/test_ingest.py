import asyncio
import hashlib

import pytest

from ingest import Chunk, IndexSync, VectorStore, chunk_words


def words(n: int, prefix: str = "w") -> str:
    return " ".join(f"{prefix}{i}" for i in range(n))


class CountingEmbedder:
    def __init__(self) -> None:
        self.texts_embedded = 0
        self.calls = 0

    async def embed(self, texts):
        self.calls += 1
        self.texts_embedded += len(texts)
        return [[float(len(t)), 1.0] for t in texts]


def test_chunks_cover_the_text_and_overlap_exactly():
    text = words(100)
    chunks = chunk_words("d", text, size=20, overlap=5)
    assert [c.chunk_id for c in chunks] == [f"d#{i}" for i in range(len(chunks))]
    assert all(text[c.start:c.end] == c.text for c in chunks), "offsets must point at the chunk text"
    for left, right in zip(chunks, chunks[1:]):
        assert left.text.split()[-5:] == right.text.split()[:5], "consecutive chunks overlap by 5 words"
    assert chunks[0].text.split()[0] == "w0" and chunks[-1].text.split()[-1] == "w99"


def test_last_window_is_not_duplicated():
    chunks = chunk_words("d", words(50), size=20, overlap=5)
    assert [(c.text.split()[0], c.text.split()[-1]) for c in chunks] == [
        ("w0", "w19"), ("w15", "w34"), ("w30", "w49")]
    assert [c.index for c in chunks] == [0, 1, 2]


@pytest.mark.parametrize("size, overlap", [(0, 0), (10, 10), (10, -1), (10, 11)])
def test_invalid_parameters(size, overlap):
    with pytest.raises(ValueError):
        chunk_words("d", "a b c", size=size, overlap=overlap)


def test_empty_text_and_content_hash():
    assert chunk_words("d", "   \n ", size=10, overlap=2) == []
    assert chunk_words("d", "", size=10, overlap=2) == []
    a = chunk_words("d", words(40), 20, 5)
    b = chunk_words("d", words(40), 20, 5)
    assert [c.content_hash for c in a] == [c.content_hash for c in b], "identical text, identical hashes"
    assert a[0].content_hash == hashlib.sha256(a[0].text.encode()).hexdigest()
    assert isinstance(a[0], Chunk)


def test_first_sync_embeds_everything_second_sync_embeds_nothing():
    emb, store = CountingEmbedder(), VectorStore()
    sync = IndexSync(emb, store, size=20, overlap=5)
    first = asyncio.run(sync.sync("d", words(100)))
    assert (first.added, first.updated, first.unchanged, first.deleted) == (7, 0, 0, 0)
    assert emb.texts_embedded == 7 and len(store) == 7
    second = asyncio.run(sync.sync("d", words(100)))
    assert (second.added, second.updated, second.unchanged, second.deleted) == (0, 0, 7, 0)
    assert emb.texts_embedded == 7 and emb.calls == 1, "an unchanged document makes zero embedder calls"


def test_editing_the_last_word_re_embeds_one_chunk():
    emb, store = CountingEmbedder(), VectorStore()
    sync = IndexSync(emb, store, size=20, overlap=5)
    asyncio.run(sync.sync("d", words(100)))
    report = asyncio.run(sync.sync("d", words(99) + " CHANGED"))
    assert (report.added, report.updated, report.unchanged) == (0, 1, 6)
    assert emb.texts_embedded == 8


def test_shrinking_a_document_deletes_orphans():
    emb, store = CountingEmbedder(), VectorStore()
    sync = IndexSync(emb, store, size=20, overlap=5)
    asyncio.run(sync.sync("d", words(100)))
    report = asyncio.run(sync.sync("d", words(50)))
    assert report.deleted == 4 and report.unchanged == 3
    assert store.ids_for("d") == {"d#0", "d#1", "d#2"}, "orphans d#3..d#6 must be removed"
    assert len(store) == 3


def test_other_documents_are_untouched():
    emb, store = CountingEmbedder(), VectorStore()
    sync = IndexSync(emb, store, size=20, overlap=5)
    asyncio.run(sync.sync("a", words(50, "a")))
    asyncio.run(sync.sync("ab", words(50, "b")))
    asyncio.run(sync.sync("a", words(10, "a")))
    assert store.ids_for("ab") == {"ab#0", "ab#1", "ab#2"}, "document a must not match document ab"
    assert store.ids_for("a") == {"a#0"}


def test_vector_store_basics():
    store = VectorStore()
    chunk = chunk_words("x", "one two three", size=5, overlap=1)[0]
    assert store.hash_of("x#0") is None and len(store) == 0
    store.upsert(chunk, [1.0])
    assert store.hash_of("x#0") == chunk.content_hash and len(store) == 1
    store.upsert(chunk, [2.0])
    assert len(store) == 1, "upsert replaces by chunk id"
    store.delete({"x#0", "missing#9"})
    assert len(store) == 0 and store.ids_for("x") == set()


def test_changes_are_embedded_in_one_batched_call():
    emb, store = CountingEmbedder(), VectorStore()
    sync = IndexSync(emb, store, size=20, overlap=5)
    asyncio.run(sync.sync("d", words(100)))
    emb.calls = 0
    report = asyncio.run(sync.sync("d", "NEW " + words(100)))
    assert report.updated + report.added > 1
    assert emb.calls == 1, "all changed chunks must go to the embedder in a single batch"
