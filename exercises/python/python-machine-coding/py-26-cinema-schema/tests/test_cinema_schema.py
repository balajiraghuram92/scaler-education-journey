import sqlite3

import pytest

from cinema_schema import (
    add_show_inventory,
    connect,
    create_schema,
    seat_counts,
    shows_in_region,
)


def make_db() -> sqlite3.Connection:
    conn = connect()
    create_schema(conn)
    conn.executescript(
        """
        INSERT INTO regions (id, name) VALUES (1, 'Bangalore'), (2, 'Mumbai');
        INSERT INTO theatres (id, name, region_id)
            VALUES (1, 'PVR Orion', 1), (2, 'INOX Nariman', 2);
        INSERT INTO screens (id, name, theatre_id) VALUES (1, 'Screen 1', 1), (2, 'Screen 1', 2);
        INSERT INTO seat_types (id, name) VALUES (1, 'GOLD'), (2, 'SILVER');
        INSERT INTO seats (id, label, screen_id, seat_type_id)
            VALUES (1, 'A1', 1, 1), (2, 'A2', 1, 1), (3, 'B1', 1, 2), (4, 'A1', 2, 1);
        INSERT INTO movies (id, name) VALUES (1, 'Inception');
        INSERT INTO shows (id, movie_id, screen_id, starts_at)
            VALUES (1, 1, 1, '2026-11-01T21:00'),
                   (2, 1, 1, '2026-11-01T18:00'),
                   (3, 1, 2, '2026-11-01T19:00');
        """
    )
    return conn


def test_foreign_keys_are_enforced():
    conn = make_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO theatres (name, region_id) VALUES ('Ghost', 999)")


def test_duplicate_seat_label_on_one_screen_rejected():
    conn = make_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO seats (label, screen_id, seat_type_id) VALUES ('A1', 1, 1)")
    # the same label on another screen is fine
    conn.execute("INSERT INTO seats (label, screen_id, seat_type_id) VALUES ('B1', 2, 1)")


def test_status_check_constraint():
    conn = make_db()
    add_show_inventory(conn, 1)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("UPDATE show_seats SET status = 'SOLD' WHERE show_id = 1")


def test_duplicate_show_seat_rejected():
    conn = make_db()
    add_show_inventory(conn, 1)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO show_seats (show_id, seat_id) VALUES (1, 1)")


def test_shows_in_region_ordered_by_start_time():
    conn = make_db()
    assert shows_in_region(conn, "Bangalore") == [2, 1]
    assert shows_in_region(conn, "Mumbai") == [3]
    assert shows_in_region(conn, "Chennai") == []


def test_inventory_is_idempotent_and_per_screen():
    conn = make_db()
    assert add_show_inventory(conn, 1) == 3
    assert add_show_inventory(conn, 1) == 0
    assert add_show_inventory(conn, 3) == 1
    assert seat_counts(conn, 1) == {"AVAILABLE": 3}


def test_seat_counts_by_status():
    conn = make_db()
    add_show_inventory(conn, 2)
    with conn:
        conn.execute("UPDATE show_seats SET status = 'BOOKED' WHERE show_id = 2 AND seat_id = 1")
        conn.execute("UPDATE show_seats SET status = 'BLOCKED' WHERE show_id = 2 AND seat_id = 2")
    assert seat_counts(conn, 2) == {"AVAILABLE": 1, "BLOCKED": 1, "BOOKED": 1}
    assert seat_counts(conn, 1) == {}


def test_connect_sets_row_factory_and_enables_foreign_keys():
    conn = connect()
    assert conn.row_factory is sqlite3.Row, "connect() must set row_factory = sqlite3.Row"
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1, "PRAGMA foreign_keys must be ON"


def test_all_eight_plural_tables_exist():
    conn = make_db()
    names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
    expected = {"regions", "theatres", "screens", "seat_types", "seats", "movies", "shows", "show_seats"}
    assert expected <= names, f"missing tables: {sorted(expected - names)}"


def test_unique_region_and_seat_type_names():
    conn = make_db()
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO regions (name) VALUES ('Bangalore')")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO seat_types (name) VALUES ('GOLD')")

