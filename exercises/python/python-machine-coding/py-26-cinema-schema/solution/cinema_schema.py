import sqlite3

SCHEMA = """
CREATE TABLE regions (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE theatres (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    region_id INTEGER NOT NULL REFERENCES regions(id)
);
CREATE TABLE screens (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    theatre_id INTEGER NOT NULL REFERENCES theatres(id)
);
CREATE TABLE seat_types (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE seats (
    id INTEGER PRIMARY KEY,
    label TEXT NOT NULL,
    screen_id INTEGER NOT NULL REFERENCES screens(id),
    seat_type_id INTEGER NOT NULL REFERENCES seat_types(id),
    UNIQUE (screen_id, label)
);
CREATE TABLE movies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE shows (
    id INTEGER PRIMARY KEY,
    movie_id INTEGER NOT NULL REFERENCES movies(id),
    screen_id INTEGER NOT NULL REFERENCES screens(id),
    starts_at TEXT NOT NULL
);
CREATE TABLE show_seats (
    id INTEGER PRIMARY KEY,
    show_id INTEGER NOT NULL REFERENCES shows(id),
    seat_id INTEGER NOT NULL REFERENCES seats(id),
    status TEXT NOT NULL DEFAULT 'AVAILABLE'
        CHECK (status IN ('AVAILABLE', 'BLOCKED', 'BOOKED')),
    UNIQUE (show_id, seat_id)
);
"""


def connect(path: str = ":memory:") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)


def add_show_inventory(conn: sqlite3.Connection, show_id: int) -> int:
    with conn:
        cur = conn.execute(
            """
            INSERT OR IGNORE INTO show_seats (show_id, seat_id)
            SELECT ?, id FROM seats
            WHERE screen_id = (SELECT screen_id FROM shows WHERE id = ?)
            """,
            (show_id, show_id),
        )
    return cur.rowcount


def shows_in_region(conn: sqlite3.Connection, region_name: str) -> list[int]:
    rows = conn.execute(
        """
        SELECT s.id
        FROM shows s
        JOIN screens sc ON sc.id = s.screen_id
        JOIN theatres t ON t.id = sc.theatre_id
        JOIN regions r ON r.id = t.region_id
        WHERE r.name = ?
        ORDER BY s.starts_at, s.id
        """,
        (region_name,),
    )
    return [row["id"] for row in rows]


def seat_counts(conn: sqlite3.Connection, show_id: int) -> dict[str, int]:
    rows = conn.execute(
        "SELECT status, COUNT(*) AS n FROM show_seats WHERE show_id = ? GROUP BY status",
        (show_id,),
    )
    return {row["status"]: row["n"] for row in rows}
