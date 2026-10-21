def count_frequency(arr: list[int]) -> dict[int, int]:
    """Return a dict mapping each distinct element of ``arr`` to its number of occurrences."""
    frequency: dict[int, int] = {}
    for element in arr:
        frequency[element] = frequency.get(element, 0) + 1
    return frequency
