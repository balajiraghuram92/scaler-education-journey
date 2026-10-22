import pytest

from bytecode_tools import (
    free_variables,
    globals_loaded_in_loops,
    is_generator_function,
    loaded_globals,
    opcode_counts,
)

LIMIT = 3


def hot(items):
    total = 0
    for x in items:
        if x > LIMIT:
            total += len(str(x))
    return total


def hoisted(items):
    limit, length, to_str = LIMIT, len, str
    total = 0
    for x in items:
        if x > limit:
            total += length(to_str(x))
    return total


def make_counter():
    n = 0

    def inc():
        nonlocal n
        n += 1
        return n

    return inc


def gen():
    yield 1


def test_loaded_globals_include_builtins_in_first_seen_order() -> None:
    assert loaded_globals(hot) == ["LIMIT", "len", "str"]


def test_globals_loaded_in_loops() -> None:
    assert globals_loaded_in_loops(hot) == ["LIMIT", "len", "str"]


def test_hoisting_moves_global_loads_out_of_the_loop() -> None:
    assert globals_loaded_in_loops(hoisted) == []
    assert set(loaded_globals(hoisted)) == {"LIMIT", "len", "str"}


def test_opcode_counts_are_names_to_positive_ints() -> None:
    counts = opcode_counts(hot)
    assert counts["LOAD_GLOBAL"] == 3
    assert counts["RETURN_VALUE"] + counts.get("RETURN_CONST", 0) >= 1
    assert all(isinstance(v, int) and v > 0 for v in counts.values())


def test_generator_and_closure_detection() -> None:
    assert is_generator_function(gen) and not is_generator_function(hot)
    assert free_variables(make_counter()) == ("n",)
    assert free_variables(hot) == ()


def test_non_function_is_rejected() -> None:
    with pytest.raises(TypeError):
        loaded_globals(42)  # type: ignore[arg-type]


def counts_with_nested(items):
    def inner():
        return len(items) + abs(1)

    return inner


def while_loop(n):
    i = 0
    total = 0
    while i < n:
        total += abs(i) + abs(-i)
        i += 1
    return total


def no_globals(a, b):
    return a + b


def test_nested_function_bytecode_is_excluded() -> None:
    assert loaded_globals(counts_with_nested) == [], "inner's LOAD_GLOBALs belong to inner's code object"
    assert "LOAD_GLOBAL" not in opcode_counts(counts_with_nested)


def test_while_loops_are_detected_and_names_are_unique() -> None:
    assert globals_loaded_in_loops(while_loop) == ["abs"], "abs is loaded twice but must be listed once"
    assert loaded_globals(while_loop) == ["abs"]
    assert loaded_globals(no_globals) == []
    assert globals_loaded_in_loops(no_globals) == []


def test_builtins_and_other_non_functions_are_rejected_everywhere() -> None:
    for tool in (opcode_counts, loaded_globals, globals_loaded_in_loops, is_generator_function, free_variables):
        with pytest.raises(TypeError):
            tool(len)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            tool("not a function")  # type: ignore[arg-type]
