from collections.abc import Iterator
from itertools import count

import pytest

from toolkit import (
    append_unique, chunked, close_enough, dedupe, make_adders, moving_average, top_k_tokens,
)


def test_append_unique_has_no_shared_default_and_respects_bucket():
    assert append_unique(1) == [1]
    assert append_unique(2) == [2], "a shared mutable default would give [1, 2]"
    bucket = [1]
    assert append_unique(1, bucket) is bucket
    assert bucket == [1], "duplicates are not appended"
    assert append_unique(2, bucket) == [1, 2]


def test_make_adders_bind_their_own_offset():
    adders = make_adders([1, 10, 100])
    assert [f(5) for f in adders] == [6, 15, 105], "late binding would give [105, 105, 105]"
    assert make_adders([]) == []


@pytest.mark.parametrize(
    ("items", "size", "expected"),
    [
        pytest.param("abcde", 2, [["a", "b"], ["c", "d"], ["e"]], id="remainder"),
        pytest.param([], 3, [], id="empty"),
        pytest.param([1, 2, 3], 3, [[1, 2, 3]], id="exact"),
        pytest.param([1, 2], 5, [[1, 2]], id="size-larger-than-input"),
        pytest.param([1, 2, 3], 1, [[1], [2], [3]], id="size-one"),
    ],
)
def test_chunked(items, size, expected):
    assert list(chunked(items, size)) == expected


def test_chunked_is_lazy_and_accepts_iterators():
    source: Iterator[int] = count()
    first = next(chunked(source, 3))
    assert first == [0, 1, 2], "must not materialise an infinite iterator"
    assert next(source) == 3, "exactly one chunk should have been consumed"
    gen = chunked(iter([1, 2, 3, 4]), 2)
    assert iter(gen) is gen, "chunked should return a generator/iterator"


@pytest.mark.parametrize("size", [0, -2], ids=["zero", "negative"])
def test_chunked_rejects_bad_size(size):
    with pytest.raises(ValueError, match="size must be >= 1"):
        list(chunked([1], size))


def test_dedupe_keeps_first_seen_order():
    assert dedupe([3, 1, 3, 2, 1]) == [3, 1, 2]
    assert dedupe([]) == []
    assert dedupe("abca") == ["a", "b", "c"]
    assert dedupe(iter([1, 1, 1])) == [1]


def test_top_k_tokens_with_ties():
    text = "the cat and The dog and the bird. And a cat!"
    assert top_k_tokens(text, 3) == [("and", 3), ("the", 3), ("cat", 2)]
    assert top_k_tokens("b a b a c", 2) == [("a", 2), ("b", 2)], "ties are broken alphabetically"


def test_top_k_tokens_edges():
    assert top_k_tokens("", 3) == []
    assert top_k_tokens("a b", 5) == [("a", 1), ("b", 1)]
    assert top_k_tokens("a b", 0) == []
    assert top_k_tokens("Don't stop, don't", 1) == [("don't", 2)], "apostrophes are part of a token"
    with pytest.raises(ValueError):
        top_k_tokens("a", -1)


def test_moving_average():
    assert moving_average([1, 2, 3, 4], 2) == [1.5, 2.5, 3.5]
    assert moving_average([1, 2], 3) == [], "no full window means no output"
    assert moving_average([0.1] * 10, 10) == [pytest.approx(0.1)]
    assert moving_average(iter([2, 4, 6]), 1) == [2, 4, 6]
    with pytest.raises(ValueError):
        moving_average([1], 0)


def test_close_enough_replaces_float_equality():
    assert 0.1 + 0.2 != 0.3
    assert close_enough(0.1 + 0.2, 0.3)
    assert not close_enough(1.0, 1.001)
    assert close_enough(0.0, 1e-13), "tiny values near zero use the absolute tolerance"
    assert close_enough(1e12, 1e12 + 1), "large values use the relative tolerance"
