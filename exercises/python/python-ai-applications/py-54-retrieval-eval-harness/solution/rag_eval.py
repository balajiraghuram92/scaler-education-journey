from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from collections.abc import Callable
from dataclasses import dataclass

Retriever = Callable[[str], list[str]]          # query -> ranked document ids (best first)


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25:
    def __init__(self, docs: dict[str, str], k1: float = 1.5, b: float = 0.75) -> None:
        self.ids = list(docs)
        tokens = [tokenize(docs[i]) for i in self.ids]
        self.k1, self.b = k1, b
        self.tf = [Counter(t) for t in tokens]
        self.lengths = [len(t) for t in tokens]
        self.avg_len = sum(self.lengths) / len(tokens)
        df = Counter(term for tf in self.tf for term in tf)
        n = len(tokens)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def rank(self, query: str) -> list[str]:
        scores = []
        terms = tokenize(query)
        for i, tf in enumerate(self.tf):
            norm = self.k1 * (1 - self.b + self.b * self.lengths[i] / self.avg_len)
            s = sum(self.idf[t] * tf[t] * (self.k1 + 1) / (tf[t] + norm) for t in terms if t in tf)
            scores.append(s)
        order = sorted(range(len(scores)), key=lambda i: (-scores[i], i))
        return [self.ids[i] for i in order]


def rrf(rankings: list[list[str]], k: int = 60) -> list[str]:
    fused: dict[str, float] = defaultdict(float)
    for ranking in rankings:
        for rank, doc in enumerate(ranking, start=1):
            fused[doc] += 1.0 / (k + rank)
    return [d for d, _ in sorted(fused.items(), key=lambda kv: (-kv[1], kv[0]))]


def hybrid(*retrievers: Retriever, rrf_k: int = 60) -> Retriever:
    return lambda query: rrf([r(query) for r in retrievers], k=rrf_k)


@dataclass(frozen=True, slots=True)
class GoldenQuery:
    query: str
    relevant: frozenset[str]


@dataclass(frozen=True, slots=True)
class Metrics:
    recall_at_k: float
    mrr: float
    ndcg_at_k: float


def ndcg_at_k(ranked: list[str], relevant: frozenset[str], k: int) -> float:
    dcg = sum(1.0 / math.log2(rank + 1) for rank, d in enumerate(ranked[:k], start=1) if d in relevant)
    ideal = sum(1.0 / math.log2(rank + 1) for rank in range(1, min(len(relevant), k) + 1))
    return dcg / ideal if ideal else 0.0


def evaluate(retriever: Retriever, golden: list[GoldenQuery], k: int = 3) -> Metrics:
    if not golden:
        raise ValueError("golden set is empty")
    recall = mrr = ndcg = 0.0
    for item in golden:
        ranked = retriever(item.query)
        recall += len(set(ranked[:k]) & item.relevant) / len(item.relevant)
        mrr += next((1.0 / r for r, d in enumerate(ranked, start=1) if d in item.relevant), 0.0)
        ndcg += ndcg_at_k(ranked, item.relevant, k)
    n = len(golden)
    return Metrics(recall / n, mrr / n, ndcg / n)


def regressions(baseline: Metrics, current: Metrics, *, tolerance: float = 0.02) -> list[str]:
    """Names of metrics that dropped by more than `tolerance`; use to fail CI."""
    bad = []
    for name in ("recall_at_k", "mrr", "ndcg_at_k"):
        if getattr(current, name) < getattr(baseline, name) - tolerance:
            bad.append(name)
    return bad
