from collections.abc import Iterable, Iterator


class Driver:
    """A driver whose identity is the ``driver_id``; ``name`` and ``rating`` may change over time.

    - ``Driver(driver_id: str, name: str, rating: float)``
    - ``driver_id`` is a read-only property; ``name`` and ``rating`` are plain attributes
    - ``__eq__`` compares ``driver_id`` only and returns ``NotImplemented`` for non-drivers
    - ``__hash__`` uses the same field, so changing ``rating`` never affects set membership
    - ``__repr__`` looks like ``Driver('D1', 'Ramesh', 4.8)``
    """

    def __init__(self, driver_id: str, name: str, rating: float) -> None:
        raise NotImplementedError("Implement Driver.__init__")

    @property
    def driver_id(self) -> str:
        raise NotImplementedError("Implement Driver.driver_id")

    def __repr__(self) -> str:
        raise NotImplementedError("Implement Driver.__repr__")

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError("Implement Driver.__eq__")

    def __hash__(self) -> int:
        raise NotImplementedError("Implement Driver.__hash__")


class DriverPool:
    """A collection that behaves like a built-in one (do not subclass ``list``).

    - ``DriverPool(drivers=())`` keeps insertion order and keeps the FIRST driver for each ID
    - ``len(pool)``; ``iter(pool)`` returns a fresh iterator every time
    - ``pool[i]`` returns a ``Driver``; ``pool[a:b]`` returns a new ``DriverPool``
    - ``x in pool`` accepts a ``Driver`` or an ID string
    - ``pool + other_pool`` is a union into a new pool; any other operand gives ``NotImplemented``
    - ``repr(pool)`` looks like ``DriverPool([Driver('D1', 'a', 4.0)])``
    - an empty pool is falsy WITHOUT defining ``__bool__``
    """

    def __init__(self, drivers: Iterable[Driver] = ()) -> None:
        raise NotImplementedError("Implement DriverPool.__init__")

    def __len__(self) -> int:
        raise NotImplementedError("Implement DriverPool.__len__")

    def __iter__(self) -> Iterator[Driver]:
        raise NotImplementedError("Implement DriverPool.__iter__")

    def __getitem__(self, index: int | slice) -> "Driver | DriverPool":
        raise NotImplementedError("Implement DriverPool.__getitem__")

    def __contains__(self, item: object) -> bool:
        raise NotImplementedError("Implement DriverPool.__contains__")

    def __add__(self, other: object) -> "DriverPool":
        raise NotImplementedError("Implement DriverPool.__add__")

    def __repr__(self) -> str:
        raise NotImplementedError("Implement DriverPool.__repr__")
