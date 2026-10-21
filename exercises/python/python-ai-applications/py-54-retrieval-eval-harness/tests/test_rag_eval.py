import math

import pytest

from rag_eval import (
    BM25,
    GoldenQuery,
    Metrics,
    evaluate,
    hybrid,
    ndcg_at_k,
    regressions,
    rrf,
)

DOCS = {
    "billing": "Invoices are generated monthly and downloadable as PDF from the billing page.",
    "retention": "Customer data is retained for 90 days after account deletion.",
    "sso": "Enterprise plans support SAML single sign on, configured in security settings.",
    "rate_limits": "The API allows 600 requests per minute and returns 429 with a Retry-After header.",
    "refunds": "Payments are returned to the original card within five business days of approval.",
    "runbook_4021": "Runbook for ERR-4021-B: restart the ingest worker and clear the dead letter queue.",
    "shipping": "Standard shipping takes three to seven business days.",
}

# A hand-written "semantic" retriever: right on paraphrases, blind to exact error codes.
DENSE = {
    "get my money back": ["refunds", "billing", "shipping", "sso", "retention", "rate_limits", "runbook_4021"],
    "ERR-4021-B": ["billing", "retention", "sso", "shipping", "rate_limits", "runbook_4021", "refunds"],
    "how often can I call the API": ["rate_limits", "sso", "billing", "retention", "shipping", "refunds", "runbook_4021"],
    "keep my login with my company directory": ["sso", "billing", "rate_limits", "retention", "shipping", "refunds", "runbook_4021"],
}
GOLDEN = [
    GoldenQuery("get my money back", frozenset({"refunds"})),
    GoldenQuery("ERR-4021-B", frozenset({"runbook_4021"})),
    GoldenQuery("how often can I call the API", frozenset({"rate_limits"})),
    GoldenQuery("keep my login with my company directory", frozenset({"sso"})),
]


def dense(query: str) -> list[str]:
    return DENSE[query]


def test_rrf_prefers_documents_ranked_well_by_both_lists():
    assert rrf([["a", "b", "c"], ["b", "c", "a"]]) == ["b", "a", "c"]


def test_rrf_ties_and_k_parameter():
    assert rrf([["a", "b"], ["b", "a"]]) == ["a", "b"], "equal scores are broken by id"
    assert rrf([]) == []
    # with k=1: x = 1/2 + 1/4 and z = 1/4 + 1/2 tie, and both beat y = 1/3 + 1/3; the tie goes to the smaller id
    assert rrf([["x", "y", "z"], ["z", "y", "x"]], k=1)[0] == "x"
    assert rrf([["a"], ["b"], ["b"]], k=60) == ["b", "a"], "documents in more lists accumulate score"


def test_bm25_finds_rare_token_and_ranks_every_document():
    ranking = BM25(DOCS).rank("ERR-4021-B")
    assert ranking[0] == "runbook_4021"
    assert sorted(ranking) == sorted(DOCS), "rank() must return all documents exactly once"


def test_bm25_ties_follow_original_document_order():
    bm25 = BM25({"first": "alpha beta", "second": "alpha beta", "third": "gamma"})
    assert bm25.rank("alpha") == ["first", "second", "third"]
    assert bm25.rank("nothing-matches") == ["first", "second", "third"], "no match keeps document order"


def test_ndcg_known_values():
    assert ndcg_at_k(["x", "a", "b"], frozenset({"a"}), 3) == pytest.approx(1 / math.log2(3))
    assert ndcg_at_k(["a", "b", "x"], frozenset({"a", "b"}), 3) == pytest.approx(1.0)
    assert ndcg_at_k(["x", "y", "z"], frozenset({"a"}), 3) == 0.0
    assert ndcg_at_k(["a"], frozenset(), 3) == 0.0, "nothing relevant gives 0.0"
    assert ndcg_at_k(["a", "b", "c"], frozenset({"a", "b", "c"}), 1) == pytest.approx(1.0), "ideal DCG is capped at k"


def test_evaluate_computes_recall_mrr_and_ndcg():
    answers = {"q1": ["x", "a", "y"], "q2": ["b", "x", "y"]}
    golden = [GoldenQuery("q1", frozenset({"a"})), GoldenQuery("q2", frozenset({"b", "c"}))]
    metrics = evaluate(lambda q: answers[q], golden, k=3)
    assert metrics.recall_at_k == pytest.approx((1.0 + 0.5) / 2)
    assert metrics.mrr == pytest.approx((0.5 + 1.0) / 2)
    first = 1 / math.log2(3)
    second = 1 / (1 + 1 / math.log2(3))
    assert metrics.ndcg_at_k == pytest.approx((first + second) / 2)
    cut = evaluate(lambda q: answers[q], golden, k=1)
    assert cut.recall_at_k == pytest.approx((0.0 + 0.5) / 2), "only the top k results count for recall"


def test_hybrid_beats_each_retriever_on_the_mixed_golden_set():
    sparse = BM25(DOCS).rank
    d = evaluate(dense, GOLDEN, k=3)
    s = evaluate(sparse, GOLDEN, k=3)
    h = evaluate(hybrid(dense, sparse), GOLDEN, k=3)
    assert d.recall_at_k < 1.0, "the dense retriever misses the exact error-code query"
    assert s.recall_at_k < 1.0, "BM25 misses the paraphrase queries"
    assert h.recall_at_k == 1.0
    assert h.recall_at_k > max(d.recall_at_k, s.recall_at_k)


def test_hybrid_composes_retrievers():
    def only(query: str) -> list[str]:
        return ["b", "a", "c"]

    assert hybrid(only)("anything") == ["b", "a", "c"], "fusing a single ranking keeps its order"
    assert callable(hybrid(only, only, rrf_k=10))


def test_evaluate_rejects_empty_golden_set():
    with pytest.raises(ValueError):
        evaluate(dense, [])


def test_regression_gate():
    base = Metrics(0.90, 0.80, 0.85)
    assert regressions(base, Metrics(0.89, 0.80, 0.85)) == [], "a drop within the tolerance passes"
    assert regressions(base, Metrics(0.80, 0.80, 0.70)) == ["recall_at_k", "ndcg_at_k"]
    assert regressions(base, Metrics(0.95, 0.90, 0.90)) == [], "improvements are fine"
    exact = Metrics(1.0, 1.0, 1.0)
    assert regressions(exact, Metrics(0.75, 1.0, 1.0), tolerance=0.25) == [], "a drop equal to the tolerance passes"
    assert regressions(exact, Metrics(0.74, 1.0, 1.0), tolerance=0.25) == ["recall_at_k"]
