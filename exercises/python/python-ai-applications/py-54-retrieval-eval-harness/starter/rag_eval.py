from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass

Retriever = Callable[[str], list[str]]  # query -> ranked document ids (best first)


def tokenize(text: str) -> list[str]:
    """Lower-cased alphanumeric tokens: ``"ERR-4021-B"`` -> ``["err", "4021", "b"]``."""
    return re.findall(r"[a-z0-9]+", text.lower())


class BM25:
    def __init__(self, docs: dict[str, str], k1: float = 1.5, b: float = 0.75) -> None:
        """Index ``docs`` (id -> text) with the Okapi BM25 parameters ``k1`` and ``b``.

        Use ``idf = log(1 + (N - df + 0.5) / (df + 0.5))`` and ``tokenize`` for both documents and queries.
        """
        raise NotImplementedError("Implement BM25.__init__")

    def rank(self, query: str) -> list[str]:
        """Return ALL document ids, best first. Ties are broken by original document order."""
        raise NotImplementedError("Implement BM25.rank")


def rrf(rankings: list[list[str]], k: int = 60) -> list[str]:
    """Reciprocal Rank Fusion: each document scores the sum of ``1 / (k + rank)`` (rank starts at 1)
    over the rankings it appears in. Ties are broken by id."""
    raise NotImplementedError("Implement rrf")


def hybrid(*retrievers: Retriever, rrf_k: int = 60) -> Retriever:
    """Return a retriever that fuses the given retrievers with ``rrf``."""
    raise NotImplementedError("Implement hybrid")


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
    """Binary-gain nDCG@k with a ``log2(rank + 1)`` discount; ``0.0`` when nothing is relevant."""
    raise NotImplementedError("Implement ndcg_at_k")


def evaluate(retriever: Retriever, golden: list[GoldenQuery], k: int = 3) -> Metrics:
    """Average recall@k, MRR and nDCG@k over the golden queries.

    Recall@k per query is ``|top-k ∩ relevant| / |relevant|``; MRR uses the first relevant rank.
    Raise ``ValueError`` for an empty golden set.
    """
    raise NotImplementedError("Implement evaluate")


def regressions(baseline: Metrics, current: Metrics, *, tolerance: float = 0.02) -> list[str]:
    """Names of metrics (``recall_at_k``, ``mrr``, ``ndcg_at_k``, in that order) that dropped
    by MORE than ``tolerance`` compared with the baseline."""
    raise NotImplementedError("Implement regressions")
