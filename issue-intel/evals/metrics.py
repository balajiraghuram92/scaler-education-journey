"""Metric functions. Pure and unit-tested; runners report, never compute."""
from __future__ import annotations


def recall_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 1.0
    return len(set(ranked[:k]) & relevant) / len(relevant)


def reciprocal_rank(ranked: list[str], relevant: set[str]) -> float:
    for i, key in enumerate(ranked, start=1):
        if key in relevant:
            return 1.0 / i
    return 0.0


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def accuracy(predicted: list[str], actual: list[str]) -> float:
    if not actual:
        return 1.0
    return sum(p == a for p, a in zip(predicted, actual, strict=True)) / len(actual)


def per_class_f1(predicted: list[str], actual: list[str], labels: list[str]) -> dict[str, float]:
    scores: dict[str, float] = {}
    for label in labels:
        tp = sum(1 for p, a in zip(predicted, actual, strict=True) if p == a == label)
        fp = sum(1 for p, a in zip(predicted, actual, strict=True) if p == label != a)
        fn = sum(1 for p, a in zip(predicted, actual, strict=True) if a == label != p)
        if tp == 0:
            scores[label] = 0.0
        else:
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            scores[label] = 2 * precision * recall / (precision + recall)
    return scores
