from config.groupAnagrams import group_anagrams


def test_groups_anagrams_in_first_seen_order():
    words = ["eat", "tea", "tan", "ate", "nat", "bat"]
    assert group_anagrams(words) == [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]


def test_empty_and_none_return_empty_list():
    assert group_anagrams([]) == []
    assert group_anagrams(None) == [], "None must return [] instead of raising"


def test_single_string():
    assert group_anagrams(["hello"]) == [["hello"]]


def test_no_anagrams_gives_one_group_per_word():
    assert group_anagrams(["abc", "def", "ghi"]) == [["abc"], ["def"], ["ghi"]]


def test_mixed_groups_keep_order_of_first_word():
    words = ["abcd", "dcba", "efgh", "hgef", "ijk", "kji"]
    assert group_anagrams(words) == [["abcd", "dcba"], ["efgh", "hgef"], ["ijk", "kji"]]
    assert group_anagrams(["kji", "x", "ijk", "x"]) == [["kji", "ijk"], ["x", "x"]]


def test_same_letters_with_different_frequencies_are_not_anagrams():
    assert group_anagrams(["aab", "abb", "baa"]) == [["aab", "baa"], ["abb"]]
    assert group_anagrams(["ab", "aab"]) == [["ab"], ["aab"]]


def test_duplicates_and_empty_strings_are_kept():
    assert group_anagrams(["", "a", "", "a"]) == [["", ""], ["a", "a"]]
    assert group_anagrams(["eat", "eat", "tea"]) == [["eat", "eat", "tea"]]


def test_does_not_mutate_input_and_returns_lists():
    words = ["tea", "eat", "bat"]
    result = group_anagrams(words)
    assert words == ["tea", "eat", "bat"], "the input list must be left untouched"
    assert isinstance(result, list) and all(isinstance(g, list) for g in result), "return a list of lists"
