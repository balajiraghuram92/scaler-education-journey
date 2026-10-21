from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from typing import Any

# Opcode names are specific to the CPython version (target 3.12 / 3.13). Use only ``dis.get_instructions`` and
# code-object attributes; do not parse ``dis.dis`` text.
#
# Every function below accepts a Python function and raises TypeError for anything without a code object
# (for example an int or a builtin such as ``len``).


def opcode_counts(func: Callable[..., Any]) -> Counter[str]:
    """Count opcodes by name in the function's OWN code object (nested functions excluded)."""
    raise NotImplementedError("Implement opcode_counts")


def loaded_globals(func: Callable[..., Any]) -> list[str]:
    """Names read through ``LOAD_GLOBAL`` (builtins such as ``len`` included), unique, in first-seen order."""
    raise NotImplementedError("Implement loaded_globals")


def globals_loaded_in_loops(func: Callable[..., Any]) -> list[str]:
    """The subset of ``loaded_globals`` whose ``LOAD_GLOBAL`` sits inside a loop body.

    Detect loops from ``JUMP_BACKWARD`` instructions: the body spans from the jump target offset to the jump's own offset.
    """
    raise NotImplementedError("Implement globals_loaded_in_loops")


def is_generator_function(func: Callable[..., Any]) -> bool:
    """True if the code object has the ``inspect.CO_GENERATOR`` flag set in ``co_flags``."""
    raise NotImplementedError("Implement is_generator_function")


def free_variables(func: Callable[..., Any]) -> tuple[str, ...]:
    """The closure variable names (``co_freevars``)."""
    raise NotImplementedError("Implement free_variables")
