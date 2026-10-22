import sqlite3

# Put the DDL for all eight tables here (regions, theatres, screens, seat_types,
# seats, movies, shows, show_seats) and run it from create_schema().
SCHEMA = """
-- TODO: CREATE TABLE statements
"""


def connect(path: str = ":memory:") -> sqlite3.Connection:
    """Open a connection with ``row_factory = sqlite3.Row`` and ``PRAGMA foreign_keys = ON``."""
    raise NotImplementedError("Implement connect")


def create_schema(conn: sqlite3.Connection) -> None:
    """Create the eight plural-named tables with foreign keys, unique constraints and the
    ``show_seats.status`` CHECK (AVAILABLE / BLOCKED / BOOKED, default AVAILABLE)."""
    raise NotImplementedError("Implement create_schema")


def add_show_inventory(conn: sqlite3.Connection, show_id: int) -> int:
    """Insert one show_seats row per seat on the show's screen, in ONE SQL statement.

    Returns the number of rows newly inserted; a second call returns 0.
    """
    raise NotImplementedError("Implement add_show_inventory")


def shows_in_region(conn: sqlite3.Connection, region_name: str) -> list[int]:
    """Show ids in the region ordered by starts_at then id (shows -> screens -> theatres -> regions)."""
    raise NotImplementedError("Implement shows_in_region")


def seat_counts(conn: sqlite3.Connection, show_id: int) -> dict[str, int]:
    """Number of show seats per status for the show (only statuses that occur)."""
    raise NotImplementedError("Implement seat_counts")
