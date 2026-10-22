from __future__ import annotations

import dis
import inspect
from collections import Counter
from collections.abc import Callable
from types import CodeType
from typing import Any


def _code(func: Callable[..., Any]) -> CodeType:
    code = getattr(func, "__code__", None)
    if not isinstance(code, CodeType):
        raise TypeError(f"{func!r} is not a Python function")
    return code


def opcode_counts(func: Callable[..., Any]) -> Counter[str]:
    """Count opcodes by name in the function's own bytecode (nested code objects excluded)."""
    return Counter(ins.opname for ins in dis.get_instructions(_code(func)))


def loaded_globals(func: Callable[..., Any]) -> list[str]:
    """Names read through LOAD_GLOBAL, unique, in first-seen order."""
    seen: dict[str, None] = {}
    for ins in dis.get_instructions(_code(func)):
        if ins.opname == "LOAD_GLOBAL":
            seen.setdefault(str(ins.argval), None)
    return list(seen)


def globals_loaded_in_loops(func: Callable[..., Any]) -> list[str]:
    """Names loaded via LOAD_GLOBAL inside a loop body, found from backward jumps."""
    instructions = list(dis.get_instructions(_code(func)))
    loops = [
        (int(ins.argval), ins.offset)
        for ins in instructions
        if ins.opname == "JUMP_BACKWARD" and isinstance(ins.argval, int)
    ]
    found: dict[str, None] = {}
    for ins in instructions:
        if ins.opname != "LOAD_GLOBAL":
            continue
        if any(start <= ins.offset <= end for start, end in loops):
            found.setdefault(str(ins.argval), None)
    return list(found)


def is_generator_function(func: Callable[..., Any]) -> bool:
    return bool(_code(func).co_flags & inspect.CO_GENERATOR)


def free_variables(func: Callable[..., Any]) -> tuple[str, ...]:
    return _code(func).co_freevars
