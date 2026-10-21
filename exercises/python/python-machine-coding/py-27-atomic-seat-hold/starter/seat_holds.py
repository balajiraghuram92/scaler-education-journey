import sqlite3
from collections.abc import Iterable, Sequence


class SeatUnavailableError(RuntimeError):
    """At least one requested seat could not be held."""


def init_inventory(path: str, show_id: int, seat_ids: Iterable[int]) -> None:
    """Create ``show_seats`` if needed and insert the seats as AVAILABLE (ignore existing ones).

    Table: show_seats(id INTEGER PRIMARY KEY, show_id INTEGER NOT NULL, seat_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'AVAILABLE', holder TEXT, UNIQUE (show_id, seat_id))
    """
    raise NotImplementedError("Implement init_inventory")


def hold_seats(path: str, show_id: int, seat_ids: Sequence[int], user: str) -> None:
    """Block every requested seat for ``user`` or change nothing.

    - open its OWN connection: ``sqlite3.connect(path, timeout=10, isolation_level=None)``
    - ``BEGIN IMMEDIATE``, then ONE compare-and-set ``UPDATE ... WHERE ... AND status = 'AVAILABLE'``
    - updated rows != number of DISTINCT requested seats -> ROLLBACK and SeatUnavailableError
    - empty ``seat_ids`` -> ValueError; unknown seats count as unavailable
    - always close the connection
    """
    raise NotImplementedError("Implement hold_seats")


def seat_states(path: str, show_id: int) -> dict[int, tuple[str, str | None]]:
    """Return ``{seat_id: (status, holder)}`` for the show."""
    raise NotImplementedError("Implement seat_states")
