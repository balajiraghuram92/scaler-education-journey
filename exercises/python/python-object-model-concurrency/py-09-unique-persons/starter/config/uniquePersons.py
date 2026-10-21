class Person:
    """Provided class. Do not modify it."""

    def __init__(self, name, age):
        self.name = name
        self.age = age


def find_unique_persons(people):
    """Return a new list with only the first ``Person`` seen for each distinct ``name``.

    - keep the first occurrence of each name; later duplicates are dropped even if their age differs
    - preserve the order of first occurrences
    - do not modify the ``Person`` class or the input list
    - run in O(n) time using a ``set`` of the names already seen
    - an empty input returns an empty list
    """
    raise NotImplementedError("Implement find_unique_persons")
