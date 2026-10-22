from typing import Any, Callable, TypeVar

# Declare a TypeVar named T and use it to annotate the signature below.


def compare(x, y, key=None):
    """Three-way comparison returning ``-1``, ``0`` or ``1``.

    Required signature (add the type hints yourself):
    ``compare(x: T, y: T, key: Callable[[T], Any] | None = None) -> int``
    where ``T`` is a ``TypeVar``.

    - without ``key``, compare ``x`` and ``y`` directly with ``<`` and ``==``
    - with ``key``, compute ``key(x)`` and ``key(y)`` exactly once each and compare those values
    - test for "no key" with ``key is not None``, not with truthiness
    - return only the integers ``-1`` (x smaller), ``0`` (equal) or ``1`` (x greater)
    - do not sort or modify the arguments
    """
    raise NotImplementedError("Implement compare")
