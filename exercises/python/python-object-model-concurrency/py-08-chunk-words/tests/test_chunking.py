import inspect
from itertools import islice

import pytest

from chunking import chunk_words


def test_basic_no_overlap():
    assert list(chunk_words(["a b c d e"], 2)) == ["a b", "c d", "e"]


def test_overlap_repeats_tail():
    assert list(chunk_words(["a b c d e f"], 3, 1)) == ["a b c", "c d e", "e f"]


def test_spans_line_boundaries_and_blank_lines():
    assert list(chunk_words(["a b", "", "c d", "e"], 3)) == ["a b c", "d e"]


def test_words_are_split_on_any_whitespace_and_joined_with_single_spaces():
    assert list(chunk_words(["  a \t b  ", "   ", "c\td"], 4)) == ["a b c d"]


def test_empty_input():
    assert list(chunk_words([], 3, 1)) == []
    assert list(chunk_words(["", "   "], 3)) == [], "only blank lines means no chunks"


def test_no_trailing_chunk_made_only_of_overlap():
    assert list(chunk_words(["a b c d"], 2, 1)) == ["a b", "b c", "c d"]
    assert list(chunk_words(["a b c d e"], 3, 2)) == ["a b c", "b c d", "c d e"]


def test_size_one_and_exact_multiples():
    assert list(chunk_words(["a b"], 1)) == ["a", "b"]
    assert list(chunk_words(["a b c d"], 2)) == ["a b", "c d"], "no extra empty chunk after an exact fit"


def test_validation_is_eager():
    with pytest.raises(ValueError):
        chunk_words(["x"], 0)  # raises without iterating
    with pytest.raises(ValueError):
        chunk_words(["x"], -2)
    with pytest.raises(ValueError):
        chunk_words(["x"], 3, 3)
    with pytest.raises(ValueError):
        chunk_words(["x"], 3, -1)
    assert not inspect.isgeneratorfunction(chunk_words), "the public function must validate before returning a generator"


def test_is_lazy_and_pulls_only_what_it_needs():
    pulled = []

    def source():
        for i in range(1000):
            pulled.append(i)
            yield "w1 w2"

    it = chunk_words(source(), 4, 1)
    assert next(it) == "w1 w2 w1 w2"
    assert len(pulled) == 2, "the first chunk needs exactly two 2-word lines"
    it.close()  # abandoning early must be safe


def test_works_with_an_endless_source():
    def endless():
        i = 0
        while True:
            yield f"{i}a {i}b"
            i += 1

    first = list(islice(chunk_words(endless(), 3, 1), 3))
    assert first == ["0a 0b 1a", "1a 1b 2a", "2a 2b 3a"]
