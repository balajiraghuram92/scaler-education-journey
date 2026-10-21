import sqlite3
from collections.abc import Iterable, Sequence


class SeatUnavailableError(RuntimeError):
    pass


def _connect(path: str) -> sqlite3.Connection:
    return sqlite3.connect(path, timeout=10, isolation_level=None)


def init_inventory(path: str, show_id: int, seat_ids: Iterable[int]) -> None:
    conn = _connect(path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS show_seats (
                id INTEGER PRIMARY KEY,
                show_id INTEGER NOT NULL,
                seat_id INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'AVAILABLE',
                holder TEXT,
                UNIQUE (show_id, seat_id)
            )
            """
        )
        conn.execute("BEGIN IMMEDIATE")
        conn.executemany(
            "INSERT OR IGNORE INTO show_seats (show_id, seat_id) VALUES (?, ?)",
            [(show_id, seat_id) for seat_id in seat_ids],
        )
        conn.execute("COMMIT")
    finally:
        conn.close()


def hold_seats(path: str, show_id: int, seat_ids: Sequence[int], user: str) -> None:
    wanted = sorted(set(seat_ids))
    if not wanted:
        raise ValueError("seat_ids must not be empty")
    placeholders = ", ".join("?" for _ in wanted)
    conn = _connect(path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        try:
            cur = conn.execute(
                f"""
                UPDATE show_seats
                SET status = 'BLOCKED', holder = ?
                WHERE show_id = ? AND seat_id IN ({placeholders}) AND status = 'AVAILABLE'
                """,
                (user, show_id, *wanted),
            )
            if cur.rowcount != len(wanted):
                raise SeatUnavailableError(f"not all of seats {wanted} are available")
            conn.execute("COMMIT")
        except BaseException:
            conn.execute("ROLLBACK")
            raise
    finally:
        conn.close()


def seat_states(path: str, show_id: int) -> dict[int, tuple[str, str | None]]:
    conn = _connect(path)
    try:
        rows = conn.execute(
            "SELECT seat_id, status, holder FROM show_seats WHERE show_id = ?", (show_id,)
        ).fetchall()
    finally:
        conn.close()
    return {seat_id: (status, holder) for seat_id, status, holder in rows}
