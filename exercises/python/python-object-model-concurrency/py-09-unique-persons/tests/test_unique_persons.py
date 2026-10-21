from config.uniquePersons import Person, find_unique_persons


def test_keeps_one_person_per_name():
    people = [Person("Alice", 30), Person("Bob", 25), Person("Alice", 35), Person("Charlie", 40)]
    result = find_unique_persons(people)
    assert [p.name for p in result] == ["Alice", "Bob", "Charlie"]


def test_keeps_the_first_occurrence_not_a_later_duplicate():
    first, second = Person("Alice", 30), Person("Alice", 35)
    result = find_unique_persons([first, Person("Bob", 25), second])
    assert result[0] is first, "the first Alice (age 30) must be kept, not a copy and not the later one"
    assert result[0].age == 30


def test_preserves_order_of_first_occurrences():
    names = ["Zed", "Amy", "Zed", "Bob", "Amy", "Cal", "Bob"]
    result = find_unique_persons([Person(n, i) for i, n in enumerate(names)])
    assert [p.name for p in result] == ["Zed", "Amy", "Bob", "Cal"]
    assert [p.age for p in result] == [0, 1, 3, 5]


def test_returns_new_list_and_does_not_modify_input():
    people = [Person("A", 1), Person("A", 2), Person("B", 3)]
    snapshot = list(people)
    result = find_unique_persons(people)
    assert result is not people, "return a new list"
    assert people == snapshot and len(people) == 3, "the input list must be left untouched"


def test_empty_and_all_unique_inputs():
    assert find_unique_persons([]) == []
    people = [Person("A", 1), Person("B", 2), Person("C", 3)]
    assert find_unique_persons(people) == people, "when all names are unique every person is kept, in order"


def test_names_are_compared_exactly():
    people = [Person("alice", 1), Person("Alice", 2), Person("alice", 3)]
    assert [p.age for p in find_unique_persons(people)] == [1, 2]


def test_person_class_is_unchanged():
    p = Person("Dee", 41)
    assert (p.name, p.age) == ("Dee", 41)


def test_runs_in_linear_time_using_a_set():
    eq_calls = 0

    class CountingName(str):
        __hash__ = str.__hash__

        def __eq__(self, other):
            nonlocal eq_calls
            eq_calls += 1
            return str.__eq__(self, other)

    n = 2000
    people = [Person(CountingName(f"name-{i}"), i) for i in range(n)]
    result = find_unique_persons(people)
    assert len(result) == n
    assert eq_calls < 10 * n, f"{eq_calls} name comparisons for {n} people: look names up in a set, not a list"
