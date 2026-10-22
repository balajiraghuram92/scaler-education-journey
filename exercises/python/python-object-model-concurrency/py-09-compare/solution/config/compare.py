from typing import Any, Callable, TypeVar

T = TypeVar('T')


def compare(x: T, y: T, key: Callable[[T], Any] | None = None) -> int:
    if key is not None:
        x_value, y_value = key(x), key(y)
    else:
        x_value, y_value = x, y

    if x_value < y_value:
        return -1
    elif x_value == y_value:
        return 0
    else:
        return 1
