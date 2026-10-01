"""Migration runner and DB pool against a throwaway pgvector container.

Skipped (with the reason shown) when Docker is unavailable.
"""

import asyncio
import os
import shutil
import subprocess
import sys
import threading

import psycopg
import pytest
from fastapi.testclient import TestClient
from pgvector import Vector
from psycopg.conninfo import conninfo_to_dict

import config
import db
import main
import migrate
from conftest import AGENT_DIR, create_lessons_stub, make_settings

REAL_FILES = ["001_enable_pgvector_extension.sql", "002_create_content_chunks.sql"]


def ledger(conninfo):
    with psycopg.connect(conninfo) as conn:
        return conn.execute("SELECT filename, applied_at FROM schema_migrations ORDER BY filename").fetchall()


def table_exists(conninfo, name):
    with psycopg.connect(conninfo) as conn:
        return conn.execute("SELECT to_regclass(%s)", (name,)).fetchone()[0] is not None


def test_fresh_db_first_run_applies_all_second_run_skips(fresh_db):
    create_lessons_stub(fresh_db)
    lines: list[str] = []

    assert migrate.run_migrations(fresh_db, log=lines.append) == REAL_FILES
    rows = ledger(fresh_db)
    assert [r[0] for r in rows] == REAL_FILES
    assert rows[0][1] != rows[1][1], "each file must commit in its own transaction"
    assert table_exists(fresh_db, "content_chunks")

    assert migrate.run_migrations(fresh_db, log=lines.append) == []
    assert ledger(fresh_db) == rows
    assert lines[-2:] == [f"{name}: already applied, skipping" for name in REAL_FILES]


def test_failing_file_keeps_earlier_commits_and_stops(fresh_db, tmp_path):
    create_lessons_stub(fresh_db)
    for name in REAL_FILES:
        shutil.copy(migrate.MIGRATIONS_DIR / name, tmp_path / name)
    (tmp_path / "003_broken.sql").write_text("CREATE TABLE half_done (id INT);\nSELECT 1/0;\n")
    (tmp_path / "004_after.sql").write_text("CREATE TABLE after_failure (id INT);\n")

    with pytest.raises(migrate.MigrationError) as err:
        migrate.run_migrations(fresh_db, migrations_dir=tmp_path, log=lambda _: None)
    assert err.value.filename == "003_broken.sql"

    assert [r[0] for r in ledger(fresh_db)] == REAL_FILES
    assert not table_exists(fresh_db, "half_done"), "failed file must roll back completely"
    assert not table_exists(fresh_db, "after_failure"), "later files must not run"

    # Fix the file and re-run: only the remaining files are applied.
    (tmp_path / "003_broken.sql").write_text("CREATE TABLE half_done (id INT);\n")
    applied = migrate.run_migrations(fresh_db, migrations_dir=tmp_path, log=lambda _: None)
    assert applied == ["003_broken.sql", "004_after.sql"]


def test_concurrent_runners_apply_each_file_once(fresh_db):
    create_lessons_stub(fresh_db)
    results, errors = [], []

    def worker():
        try:
            results.append(migrate.run_migrations(fresh_db, log=lambda _: None))
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=60)
    assert not errors
    assert sorted(name for run in results for name in run) == REAL_FILES


def test_cli_from_other_cwd_with_special_char_password(pg_server, fresh_db, tmp_path):
    create_lessons_stub(fresh_db)
    dbname = conninfo_to_dict(fresh_db)["dbname"]
    password = "p@ss:w/rd#50%'x"
    with psycopg.connect(fresh_db, autocommit=True) as conn:
        conn.execute(f"CREATE ROLE migrator LOGIN SUPERUSER PASSWORD '{password.replace(chr(39), chr(39) * 2)}'")
    env = {k: v for k, v in os.environ.items() if not k.startswith("DATABASE_")}
    env.update(
        DATABASE_HOST=pg_server["host"],
        DATABASE_PORT=pg_server["port"],
        DATABASE_NAME=dbname,
        DATABASE_USER="migrator",
        DATABASE_PASSWORD=password,
    )
    result = subprocess.run(
        [sys.executable, str(AGENT_DIR / "migrate.py")],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "001_enable_pgvector_extension.sql: applied" in result.stdout
    assert "migrate: done (2 applied)" in result.stdout
    with psycopg.connect(fresh_db, autocommit=True) as conn:
        conn.execute("DROP OWNED BY migrator; REASSIGN OWNED BY migrator TO postgres")


def test_pool_works_before_vector_exists_and_after_migration(fresh_db):
    create_lessons_stub(fresh_db)

    async def query_once():
        pool = db.create_pool(fresh_db)
        await pool.open(wait=True, timeout=10)
        try:
            async with pool.connection(timeout=5) as conn:
                cur = await conn.execute("SELECT 1")
                return await cur.fetchone()
        finally:
            await pool.close()

    # Brand-new DB without the vector type: no deadlock / PoolTimeout.
    assert asyncio.run(query_once()) == (1,)

    # Readiness endpoint on the real DB reports the missing extension, then migrate.
    app = main.build_app(make_settings(database_conninfo=fresh_db))
    with TestClient(app) as client:
        body = client.get("/health/ready").json()
    assert body == {"status": "ready", "database": "ok", "vector_extension": False}

    migrate.run_migrations(fresh_db, log=lambda _: None)

    async def vector_roundtrip():
        pool = db.create_pool(fresh_db)
        await pool.open(wait=True, timeout=10)
        try:
            async with pool.connection(timeout=5) as conn:
                cur = await conn.execute("SELECT %s::vector", (Vector([1.0, 2.0, 3.0]),))
                return (await cur.fetchone())[0]
        finally:
            await pool.close()

    # A Vector (not a str) proves the adapters were registered on the new connection.
    result = asyncio.run(vector_roundtrip())
    assert isinstance(result, Vector)
    assert result.to_list() == [1.0, 2.0, 3.0]
    app = main.build_app(make_settings(database_conninfo=fresh_db))
    with TestClient(app) as client:
        assert client.get("/health/ready").json()["vector_extension"] is True


def test_settings_from_parts_connect_to_real_db(pg_server, fresh_db):
    parts = conninfo_to_dict(fresh_db)
    settings = config.load_settings(
        {
            "JWT_SIGNING_KEY": "k" * 32,
            "MUSE_AI_API_KEY": "m",
            "DATABASE_HOST": parts["host"],
            "DATABASE_PORT": parts["port"],
            "DATABASE_NAME": parts["dbname"],
            "DATABASE_USER": parts["user"],
            "DATABASE_PASSWORD": parts["password"],
        }
    )
    with psycopg.connect(settings.database_conninfo) as conn:
        assert conn.execute("SELECT current_database()").fetchone()[0] == parts["dbname"]
