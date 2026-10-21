from collections import Counter

from config.countFreq import count_frequency


def test_counts_mixed_list():
    assert count_frequency([1, 2, 3, 4, 1, 2, 3, 1, 2, 1]) == {1: 4, 2: 3, 3: 2, 4: 1}


def test_empty_list_returns_empty_dict():
    assert count_frequency([]) == {}


def test_single_element():
    assert count_frequency([5]) == {5: 1}


def test_returns_a_dict():
    result = count_frequency([7, 7])
    assert type(result) is dict, "return a plain dict, not a Counter or another mapping"
    assert result == {7: 2}


def test_input_is_not_mutated():
    data = [3, 1, 3]
    count_frequency(data)
    assert data == [3, 1, 3]


def test_does_not_print(capsys):
    count_frequency([1, 1, 2])
    assert capsys.readouterr().out == ""


def test_handles_zero_and_negatives():
    data = [0, -1, -1, 0, 0, 5]
    assert count_frequency(data) == dict(Counter(data))
