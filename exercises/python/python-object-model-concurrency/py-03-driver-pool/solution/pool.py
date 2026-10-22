from collections.abc import Iterable, Iterator
from typing import overload


class Driver:
    """Identity is the driver_id; name and rating may change over time."""

    def __init__(self, driver_id: str, name: str, rating: float) -> None:
        self._driver_id = driver_id
        self.name = name
        self.rating = rating

    @property
    def driver_id(self) -> str:
        return self._driver_id

    def __repr__(self) -> str:
        return f"Driver({self._driver_id!r}, {self.name!r}, {self.rating!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Driver):
            return NotImplemented
        return self._driver_id == other._driver_id

    def __hash__(self) -> int:
        return hash(self._driver_id)


class DriverPool:
    def __init__(self, drivers: Iterable[Driver] = ()) -> None:
        seen: dict[str, Driver] = {}
        for d in drivers:
            seen.setdefault(d.driver_id, d)          # first occurrence wins
        self._drivers: list[Driver] = list(seen.values())

    def __len__(self) -> int:
        return len(self._drivers)

    def __iter__(self) -> Iterator[Driver]:
        return iter(self._drivers)                   # a fresh iterator every time

    @overload
    def __getitem__(self, index: int) -> Driver: ...
    @overload
    def __getitem__(self, index: slice) -> "DriverPool": ...
    def __getitem__(self, index: int | slice) -> "Driver | DriverPool":
        if isinstance(index, slice):
            return DriverPool(self._drivers[index])
        return self._drivers[index]

    def __contains__(self, item: object) -> bool:
        if isinstance(item, str):
            return any(d.driver_id == item for d in self._drivers)
        return item in self._drivers

    def __add__(self, other: object) -> "DriverPool":
        if not isinstance(other, DriverPool):
            return NotImplemented
        return DriverPool([*self._drivers, *other._drivers])

    def __repr__(self) -> str:
        return f"DriverPool({self._drivers!r})"
