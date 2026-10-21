# Retrieval-Augmented Generation Pipelines in Python

Retrieval-augmented generation (RAG) is how most production LLM features get grounded in private, current data: find the relevant passages, put them in the prompt, and make the model answer from them with citations. The demo takes an afternoon; the production system takes months, because quality is decided by dull engineering: how you chunk, what you index, how you combine keyword and vector search, how you measure, and how you keep the index in sync with reality. In AI and FDE interviews, "walk me through a RAG pipeline and tell me how you know it works" is close to a guaranteed question.

## Concepts Covered

### The pipeline and where it fails

A RAG system has an **offline path** (load, clean, chunk, embed, index) and an **online path** (embed the query, retrieve, optionally rerank, assemble the prompt, generate, verify). Failures are usually retrieval failures: if the right passage is not in the context, no prompt can save the answer. So the discipline is to evaluate retrieval and generation separately, as the last sections show. All the code below runs on the standard library plus NumPy, with a deterministic stand-in for the embedding API so you can execute it offline.

### Ingestion: loading, cleaning and chunking

Cleaning removes noise that hurts both keyword and vector search (non-breaking spaces, runs of blank lines, navigation boilerplate). Chunking decides what a "passage" is. Chunks that are too large dilute the embedding and waste prompt tokens; chunks that are too small lose context. Common strategies, in rough order of sophistication:

- **Fixed-size windows with overlap** (by tokens or words): simple, predictable, and overlap prevents a sentence that straddles a boundary from being lost.
- **Structure-aware splitting:** split on headings, paragraphs or code blocks first, then pack pieces up to a size limit. Better for documentation and contracts.
- **Semantic or sentence-based splitting:** break where topic similarity drops. More expensive, with uneven benefits, so measure before adopting.

Always store provenance with each chunk: document id, position and character offsets, so you can cite, highlight and delete or refresh precisely.

```python
from __future__ import annotations

import asyncio
import hashlib
import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(frozen=True, slots=True)
class Chunk:
    chunk_id: str
    doc_id: str
    index: int
    text: str
    start: int          # character offsets into the cleaned document (for citations/highlighting)
    end: int


def clean_text(raw: str) -> str:
    text = raw.replace("\r\n", "\n").replace(" ", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_words(doc_id: str, text: str, size: int = 120, overlap: int = 20) -> list[Chunk]:
    if not 0 <= overlap < size:
        raise ValueError("need 0 <= overlap < size")
    spans = [m.span() for m in re.finditer(r"\S+", text)]
    chunks: list[Chunk] = []
    for i, first in enumerate(range(0, len(spans), size - overlap)):
        window = spans[first:first + size]
        start, end = window[0][0], window[-1][1]
        chunks.append(Chunk(f"{doc_id}#{i}", doc_id, i, text[start:end], start, end))
        if first + size >= len(spans):
            break
    return chunks
```

On a 50-word document with `size=20, overlap=5`, the chunks cover words `w0..w19`, `w15..w34` and `w30..w49`: three chunks, each sharing five words with its neighbour, with character spans `0-69`, `50-129` and `110-189`. `clean_text("Refunds take   5 days.\r\n\r\n\r\n\r\nContact  us.  ")` returns `'Refunds take 5 days.\n\nContact us.'`. Overlap has a price: with 1,000 words, `size=120, overlap=20` gives 10 chunks but `overlap=100` gives 45, so index size and embedding cost grow about 4.5 times for the same text.

### Embeddings in batches

Embedding APIs take a list of inputs per request and are rate limited, so you batch, run a few batches concurrently under a semaphore, and preserve order (`asyncio.gather` returns results in input order). Normalise vectors to unit length once at ingestion so that cosine similarity becomes a plain dot product. Cache by a hash of model name plus text, because re-embedding unchanged chunks on every deploy is the most common way to waste money, and because changing the embedding model invalidates every vector, so the model name belongs in the key and in the index metadata.

```python
TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())


class Embedder(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class HashEmbedder:
    """Deterministic stand-in for a real embedding API: signed hashed bag-of-words.
    It is lexical, NOT semantic; it exists so the pipeline is runnable offline."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    async def embed(self, texts: list[str]) -> list[list[float]]:
        out = []
        for text in texts:
            v = np.zeros(self.dim)
            for tok in tokenize(text):
                h = int.from_bytes(hashlib.blake2b(tok.encode(), digest_size=8).digest(), "big")
                v[h % self.dim] += 1.0 if (h >> 63) & 1 else -1.0
            out.append(v.tolist())
        return out


async def embed_all(embedder: Embedder, texts: list[str], *, batch_size: int = 64,
                    concurrency: int = 4) -> np.ndarray:
    sem = asyncio.Semaphore(concurrency)

    async def one(batch: list[str]) -> list[list[float]]:
        async with sem:
            return await embedder.embed(batch)

    batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
    results = await asyncio.gather(*(one(b) for b in batches))      # gather keeps input order
    mat = np.asarray([vec for res in results for vec in res], dtype=np.float32)
    return mat / np.maximum(np.linalg.norm(mat, axis=1, keepdims=True), 1e-12)


class CachedEmbedder:
    def __init__(self, inner: Embedder, model: str) -> None:
        self._inner, self._model = inner, model
        self._cache: dict[str, list[float]] = {}

    def _key(self, text: str) -> str:
        return hashlib.sha256(f"{self._model}\x00{text}".encode()).hexdigest()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        missing = [t for t in dict.fromkeys(texts) if self._key(t) not in self._cache]
        if missing:
            for text, vec in zip(missing, await self._inner.embed(missing)):
                self._cache[self._key(text)] = vec
        return [self._cache[self._key(t)] for t in texts]
```

Embedding 150 texts with `batch_size=64` makes 3 provider calls and returns a `(150, 256)` `float32` matrix whose rows have norm `1.0`. Behind `CachedEmbedder`, a call with `["a", "b", "a"]` sends only the two distinct texts to the inner embedder, a later call with `["b", "cc"]` sends only `["cc"]`, and a third call for `["a"]` sends nothing.

### Vector search: exact first, approximate later

With unit-length vectors, cosine similarity is `matrix @ query`. For up to a few hundred thousand vectors, this brute-force scan in NumPy is fast, exact and trivial to reason about, and it is the right baseline to measure against. `np.argpartition` selects the top k in linear time, and then you sort only those k.

```python
def top_k_cosine(matrix: np.ndarray, query: np.ndarray, k: int) -> list[tuple[int, float]]:
    """matrix rows must be unit-length; cosine similarity is then a dot product."""
    q = query / max(float(np.linalg.norm(query)), 1e-12)
    scores = matrix @ q
    k = min(k, len(scores))
    idx = np.argpartition(-scores, k - 1)[:k]            # O(n) selection, then sort only k
    idx = idx[np.argsort(-scores[idx])]
    return [(int(i), float(scores[i])) for i in idx]
```

Searching the identity matrix `np.eye(3)` with query `[0.2, 0.9, 0.1]` and `k=2` gives row 1 with similarity about `0.97` and row 0 with about `0.22`. If the rows were not normalised, a long vector would win on raw dot product regardless of direction, so normalise or use a distance metric that does.

When the corpus grows to millions of vectors, you trade exactness for speed with an **approximate nearest neighbour (ANN)** index. The ideas worth knowing for an interview: graph indexes such as HNSW navigate a layered proximity graph greedily and give high recall at low latency but use a lot of memory; inverted-file (IVF) indexes cluster vectors and search only the nearest clusters; product quantisation (PQ) compresses vectors to cut memory at some accuracy cost. Each exposes a recall-versus-latency knob (such as a search-time beam width or the number of clusters probed), so you tune it against your own labelled queries. Metadata filters (tenant, language, date) interact with ANN: filtering after the search can leave too few results, so check how your store applies filters.

### Hybrid search: BM25 plus vectors, fused with RRF

Dense vectors capture paraphrase ("get my money back" matches "refund") but are weak on exact tokens such as error codes, SKUs, names and rare jargon. **BM25** is the classic keyword scorer: term frequency with saturation, inverse document frequency, and length normalisation. The two fail on different queries, so production systems run both and fuse the rankings. Raw scores are not comparable (cosine is in [-1, 1], BM25 is unbounded), so fuse by **rank** with Reciprocal Rank Fusion: each list contributes `1 / (k + rank)`, with `k` around 60.

```python
class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75) -> None:
        self.k1, self.b = k1, b
        self.tf = [Counter(d) for d in docs]
        self.lengths = [len(d) for d in docs]
        self.avg_len = sum(self.lengths) / len(docs)
        df = Counter(term for tf in self.tf for term in tf)
        n = len(docs)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def scores(self, query: list[str]) -> list[float]:
        out = [0.0] * len(self.tf)
        for i, tf in enumerate(self.tf):
            norm = self.k1 * (1 - self.b + self.b * self.lengths[i] / self.avg_len)
            for term in query:
                f = tf.get(term, 0)
                if f:
                    out[i] += self.idf[term] * f * (self.k1 + 1) / (f + norm)
        return out


def rank_of(scores: list[float]) -> list[int]:
    return sorted(range(len(scores)), key=lambda i: -scores[i])


def rrf(rankings: list[list[int]], k: int = 60) -> list[tuple[int, float]]:
    """Reciprocal Rank Fusion: score-scale free, so BM25 and cosine can be combined."""
    fused: dict[int, float] = defaultdict(float)
    for ranking in rankings:
        for rank, doc in enumerate(ranking, start=1):
            fused[doc] += 1.0 / (k + rank)
    return sorted(fused.items(), key=lambda kv: -kv[1])
```

`rrf([[0, 1, 2], [1, 2, 0]])` returns `[(1, 0.03252...), (0, 0.03226...), (2, 0.03200...)]`: document 1 is ranked first and second, so it beats document 0, which is first and last. In production, BM25 usually comes from the search engine or database (PostgreSQL full-text search, OpenSearch) rather than a Python class; the point of writing it once is to understand the knobs `k1` and `b`.

### Reranking

First-stage retrieval is built for recall over millions of items, so it uses cheap, independent embeddings. A **reranker**, typically a cross-encoder model that reads the query and a passage together, is far more precise but too slow to run on everything. The standard shape is two stages: fuse to get the top 30 to 100 candidates, rerank, keep the top 3 to 8 for the prompt.

```python
class Reranker(Protocol):
    async def score(self, query: str, passages: list[str]) -> list[float]: ...


@dataclass(slots=True)
class Index:
    chunks: list[Chunk]
    matrix: np.ndarray          # (n_chunks, dim), unit-length rows
    bm25: BM25


async def retrieve(index: Index, embedder: Embedder, reranker: Reranker | None, query: str,
                   *, k_each: int = 30, k_final: int = 5) -> list[Chunk]:
    qvec = np.asarray((await embedder.embed([query]))[0], dtype=np.float32)
    dense = [i for i, _ in top_k_cosine(index.matrix, qvec, k_each)]
    sparse = rank_of(index.bm25.scores(tokenize(query)))[:k_each]
    candidates = [i for i, _ in rrf([dense, sparse])][:k_each]            # cheap recall stage
    if reranker is not None:                                              # precise, slower stage
        scores = await reranker.score(query, [index.chunks[i].text for i in candidates])
        candidates = [i for _, i in sorted(zip(scores, candidates), reverse=True)]
    return [index.chunks[i] for i in candidates[:k_final]]
```

### Prompt assembly with citations

Number the sources, instruct the model to answer only from them, to cite as `[n]`, and to say it does not know otherwise. Respect a context budget: drop the lowest-ranked chunks, never truncate one mid-sentence silently. Then **verify**: every cited number must refer to a source you supplied, and each claim should be supported by the chunk it cites. A lexical overlap check is only a smoke test; production faithfulness usually uses an LLM judge or a trained entailment model, calibrated against human labels.

```python
SYSTEM = ("Answer using ONLY the numbered sources. Cite every claim as [n]. "
          "If the sources do not contain the answer, reply exactly: I don't know.")


def build_messages(question: str, chunks: list[Chunk], max_chars: int = 6000
                   ) -> tuple[list[dict[str, str]], list[Chunk]]:
    used_chunks: list[Chunk] = []
    blocks: list[str] = []
    size = 0
    for chunk in chunks:
        block = f"[{len(blocks) + 1}] (source: {chunk.doc_id}) {chunk.text}"
        if size + len(block) > max_chars:
            break
        blocks.append(block)
        used_chunks.append(chunk)
        size += len(block)
    user = "SOURCES:\n" + "\n\n".join(blocks) + f"\n\nQUESTION: {question}"
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}], used_chunks


CITE = re.compile(r"\[(\d+)\]")
STOP = frozenset("the a an of to in is are and or for on with by it that this as be at from".split())


def check_answer(answer: str, sources: list[Chunk]) -> dict[str, object]:
    """Cheap faithfulness smoke test: valid citations + lexical support per sentence."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", answer) if s.strip()]
    invalid: set[int] = set()
    supported = 0
    for sent in sentences:
        cited = {int(n) for n in CITE.findall(sent)}
        invalid |= {n for n in cited if not 1 <= n <= len(sources)}
        words = {w for w in tokenize(CITE.sub("", sent)) if w not in STOP}
        evidence = {w for n in cited if 1 <= n <= len(sources) for w in tokenize(sources[n - 1].text)}
        if cited and words and len(words & evidence) / len(words) >= 0.6:
            supported += 1
    return {"invalid_citations": sorted(invalid),
            "supported_sentences": f"{supported}/{len(sentences)}"}
```

With a refunds chunk as source `[1]`, the grounded answer `"Refunds go to the original payment method within 5 business days [1]."` gives `{'invalid_citations': [], 'supported_sentences': '1/1'}`, while `"Refunds are instant [1]. Express shipping is free [3]."` gives `{'invalid_citations': [3], 'supported_sentences': '0/2'}`: one hallucinated citation and no supported sentence.

> **Production note:** Retrieved text is untrusted input. A document can contain instructions aimed at the model. Keep tools least-privileged, keep sources clearly delimited, and never let retrieved content widen what the user is allowed to see: apply tenant and ACL filters in the retrieval query itself.

### Evaluation: measure retrieval and generation separately

Build a **golden set** of real questions with the chunk or document ids that answer them. Then measure retrieval with **recall@k** (the fraction of relevant items in the top k), **MRR** (mean reciprocal rank of the first relevant hit) and, where grades exist, nDCG. Measure generation with faithfulness (is every claim supported by the cited context?), answer relevance, and citation validity. Run the set in CI so a chunking or model change cannot silently regress quality.

```python
def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / rank
    return 0.0
```

For ranking `["a", "b", "c", "d"]` and relevant set `{"c", "z"}`, `recall_at_k(..., 3)` is `0.5` (one of two relevant items found), `recall_at_k(..., 2)` is `0.0`, and the reciprocal rank is `0.333`. Running a harness like this over eight tiny support documents and six paraphrased questions with the lexical hash embedder gave `recall@1 / MRR` of `0.33 / 0.60` for dense, `0.83 / 0.87` for BM25 and `0.67 / 0.79` for the RRF hybrid. Do not read those numbers as a verdict on hybrid search: the stand-in embedder is lexical, not semantic, and the corpus is tiny. The lesson is that the harness gives you numbers you can compare before and after every change, and that you must evaluate with real embeddings on your own data.

### Caching and freshness

Cache at three levels: embeddings (key: model + text hash), retrieval results (key: normalised query + index version, short TTL), and full answers where questions repeat. Every cache key must include the **index version**, otherwise a re-ingest serves stale answers. For freshness, give chunks deterministic ids (`doc_id#index`) plus a content hash, upsert changed chunks, and delete chunk ids that no longer exist: a document that shrinks from ten chunks to seven leaves three orphans that will keep being retrieved.

> **Interview tip:** When asked how to improve a RAG system, start with measurement: look at failures, label whether retrieval or generation failed, and fix the stage that failed. Chunking, hybrid search and reranking are common retrieval fixes; prompt changes only help when the right context was retrieved.

## Practical Backend Scenario

You are the forward-deployed engineer for an insurer whose adjusters ask questions over 40,000 policy PDFs. The first pilot used 1,000-word chunks and vector search only. Adjusters complained that clause numbers ("Section 7.3(b)") and product codes were never found, and answers cited clauses from the wrong policy version. The fix: structure-aware chunking by clause with the policy id, version and clause path stored as metadata; hybrid retrieval so exact clause numbers match through BM25; a reranker on the top 40; version and tenant filters applied inside the retrieval query; and a golden set of 150 adjuster questions run in CI, reporting recall@5, MRR, citation validity and a faithfulness score. Re-ingestion became incremental, keyed by content hash, with orphan chunk deletion.

## Practice Loop

1. Run `chunk_words` on a 1,000-word document with `overlap=20` and `overlap=100`; compare the chunk counts and explain the cost.
2. Implement `embed_all` and `CachedEmbedder`; count provider calls for 150 texts and prove a repeat run makes none.
3. Write `top_k_cosine` and test it on a hand-built matrix; then run it unnormalised and observe the ranking change.
4. Implement `BM25` and `rrf`, then build a six-question golden set over eight short documents and print recall@1 and MRR for dense, BM25 and hybrid.
5. Add a query that contains a rare token (an error code) and see which retriever finds it.
6. Build the prompt with `build_messages` and run `check_answer` on a grounded and a hallucinated answer.
7. Simulate re-ingestion of a document that shrinks, and write the code that removes the orphan chunk ids.

## Evidence of Understanding

- I can explain how chunk size and overlap trade context against precision and cost, and what provenance metadata I store.
- I can explain why vectors are normalised and when brute-force NumPy search is enough.
- I can describe the idea behind HNSW, IVF and PQ and the recall-versus-latency knob each exposes.
- I can explain why RRF fuses ranks instead of raw scores, and when BM25 beats dense search.
- I can describe the two-stage retrieve-then-rerank design.
- I can compute recall@k and reciprocal rank by hand and say what faithfulness measures that recall does not.
- I can describe how to keep an index fresh without orphans or stale cache hits.

## Interview Questions to Rehearse

### Q: How do you choose chunk size and overlap?
Treat them as hyperparameters measured on a golden set. Start around 200 to 500 tokens with 10 to 20 percent overlap, prefer structure-aware splits (headings, clauses) for documents that have structure, and check recall@k at each setting. Larger chunks carry context but dilute embeddings and cost prompt tokens; overlap protects boundaries but multiplies index size.

### Q: Why hybrid search, and why RRF?
Dense retrieval handles paraphrase; BM25 handles exact and rare tokens. They fail on different queries, so combining raises recall. Their scores are on incompatible scales, so I fuse ranks with Reciprocal Rank Fusion, which needs no calibration and is robust, then optionally rerank the fused top candidates.

### Q: How do you evaluate a RAG system?
Separately for retrieval and generation. Retrieval: recall@k and MRR on a golden set of real questions with labelled relevant chunks. Generation: faithfulness to the cited context, citation validity, and answer relevance, using an LLM judge calibrated against human review plus cheap deterministic checks. Run it in CI and track it per release and per prompt or model version.

### Q: When do you move from NumPy brute force to an ANN index?
When latency or memory with exact search stops meeting the target, typically beyond a few hundred thousand to a few million vectors depending on dimension and hardware. I first measure exact-search latency, then choose an index, and tune its recall knob against the exact results on my own queries so I know what recall I am giving up.

### Q: Users see answers based on an outdated policy. Where do you look?
Index freshness: content hashes and upserts, orphan chunk deletion, version metadata and filters, and cache keys that include the index version. Then check whether retrieval ranks the old version above the new, and whether the prompt tells the model to prefer the latest effective date.

## Common Pitfalls

- Evaluating only the final answer, so retrieval regressions hide behind fluent text.
- Chunking by raw character count mid-sentence, with no provenance metadata.
- Mixing embeddings from different models or versions in one index.
- Not normalising vectors, then comparing dot products as if they were cosines.
- Combining BM25 and cosine by adding raw scores.
- Retrieval without tenant and ACL filters, which leaks documents across users.
- Stuffing every retrieved chunk into the prompt rather than reranking and budgeting.
- Cache keys without the index version, serving stale answers after re-ingest.
- Leaving orphan chunks after documents shrink or are deleted.
- Trusting a model's `[n]` citations without checking they refer to supplied sources.

## Suggested Extension

Add a faithfulness judge: a function that takes the answer and the cited chunks, asks a model (through your typed client) to label each sentence as supported, partially supported or unsupported, and returns a score. Calibrate it on 30 hand-labelled answers, report its agreement with you, and wire it into your CI evaluation alongside recall@k and MRR.
