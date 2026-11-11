"""Unit tests for pure metric functions."""
from __future__ import annotations

from evals.metrics import accuracy, mean, per_class_f1, recall_at_k, reciprocal_rank


def test_recall_at_k() -> None:
    assert recall_at_k(["a", "b", "c"], {"b"}, 2) == 1.0
    assert recall_at_k(["a", "b", "c"], {"c"}, 2) == 0.0
    assert recall_at_k(["a", "b"], {"a", "b"}, 1) == 0.5
    assert recall_at_k([], set(), 5) == 1.0


def test_reciprocal_rank() -> None:
    assert reciprocal_rank(["a", "b"], {"b"}) == 0.5
    assert reciprocal_rank(["a"], {"z"}) == 0.0


def test_mean_and_accuracy() -> None:
    assert mean([1.0, 0.0]) == 0.5
    assert mean([]) == 0.0
    assert accuracy(["a", "b"], ["a", "c"]) == 0.5
    assert accuracy([], []) == 1.0


def test_per_class_f1() -> None:
    predicted = ["a", "a", "b", "b"]
    actual = ["a", "b", "b", "b"]
    scores = per_class_f1(predicted, actual, ["a", "b"])
    assert scores["a"] == 2 * (0.5 * 1.0) / (0.5 + 1.0)
    assert scores["b"] == 2 * (1.0 * (2 / 3)) / (1.0 + (2 / 3))
    assert per_class_f1(["a"], ["b"], ["c"]) == {"c": 0.0}
