from collections import defaultdict


def group_anagrams(strs):
    if not strs:
        return []

    anagrams = defaultdict(list)

    # Group anagrams using a dictionary keyed by the sorted letters
    for s in strs:
        sorted_s = ''.join(sorted(s))
        anagrams[sorted_s].append(s)

    return list(anagrams.values())
