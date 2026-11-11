import os
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SERVICE_DIR = Path(__file__).resolve().parent.parent
if str(SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(SERVICE_DIR))

import app.main  # noqa: E402
from app import db as db_module  # noqa: E402
from app.providers.fake import FakeChatProvider, FakeEmbeddingProvider  # noqa: E402
from app.settings import Settings  # noqa: E402

TEST_SECRET = "unit-test-shared-secret"
PGVECTOR_IMAGE = os.environ.get("LOCALIZATION_AI_TEST_PG_IMAGE", "pgvector/pgvector:pg16")
SCHEMA_SQL = Path(__file__).resolve().parent / "schema.sql"


def make_settings(**overrides) -> Settings:
    values = dict(
        api_shared_secret=TEST_SECRET,
        # Nothing listens on port 1; the pool is never opened in unit tests.
        database_host="127.0.0.1",
        database_port=1,
        database_name="none",
        database_user="none",
        database_password="none",
    )
    values.update(overrides)
    return Settings(**values)


def auth_headers(secret: str = TEST_SECRET) -> dict:
    return {"x-api-key": secret}


@pytest.fixture
def settings() -> Settings:
    return make_settings()


@pytest.fixture
def application(settings):
    return app.main.build_app(
        settings,
        chat_provider=FakeChatProvider(),
        embedding_provider=FakeEmbeddingProvider(),
    )


@pytest.fixture
def client(application):
    # No `with`: lifespan (pool open, COMET load) is not started in unit tests.
    return TestClient(application)


# ---------------------------------------------------------------- docker / pgvector


def _docker_unavailable_reason() -> str | None:
    if not shutil.which("docker"):
        return "docker CLI not installed"
    probe = subprocess.run(["docker", "info"], capture_output=True, text=True)
    if probe.returncode != 0:
        return "docker daemon not reachable"
    return None


@pytest.fixture(scope="session")
def pg_server():
    """Throwaway pgvector container; yields admin conninfo parts. Never a real DB."""
    reason = _docker_unavailable_reason()
    if reason:
        pytest.skip(f"DB tests need Docker: {reason}")
    name = f"localization-ai-test-pg-{uuid.uuid4().hex[:8]}"
    password = "throwaway-" + uuid.uuid4().hex
    subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--rm",
            "--name",
            name,
            "-e",
            f"POSTGRES_PASSWORD={password}",
            "-p",
            "127.0.0.1::5432",
            PGVECTOR_IMAGE,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    try:
        port = (
            subprocess.run(["docker", "port", name, "5432/tcp"], check=True, capture_output=True, text=True)
            .stdout.strip()
            .splitlines()[0]
            .rsplit(":", 1)[1]
        )
        server = {"host": "127.0.0.1", "port": port, "user": "postgres", "password": password}
        import psycopg

        deadline = time.monotonic() + 60
        while True:
            try:
                with psycopg.connect(dbname="postgres", connect_timeout=2, **server):
                    break
            except psycopg.OperationalError:
                if time.monotonic() > deadline:
                    raise
                time.sleep(0.5)
        yield server
    finally:
        subprocess.run(["docker", "rm", "-f", name], capture_output=True)


@pytest.fixture
def fresh_db(pg_server):
    """A brand-new database with the LA1-shaped test schema. Yields a conninfo string."""
    import psycopg
    from psycopg.conninfo import make_conninfo

    dbname = "t_" + uuid.uuid4().hex[:10]
    with psycopg.connect(dbname="postgres", autocommit=True, **pg_server) as admin:
        admin.execute(f'CREATE DATABASE "{dbname}"')
    conninfo = make_conninfo(dbname=dbname, **pg_server)
    with psycopg.connect(conninfo, autocommit=True) as conn:
        conn.execute(SCHEMA_SQL.read_text(encoding="utf-8"))
    yield conninfo
    with psycopg.connect(dbname="postgres", autocommit=True, **pg_server) as admin:
        admin.execute(f'DROP DATABASE IF EXISTS "{dbname}" WITH (FORCE)')


@pytest.fixture
def seeded_project_id(fresh_db):
    """One project with two de-DE golden cases and two glossary terms.

    Returns (conninfo, project_id). The seed is the hand-computed scenario
    used by the runner test:

    - glossary: HUD->HUD, "Turn left"->"Links abbiegen" (both de-DE)
    - case 1: source "Turn left", gold "Links abbiegen" (short-label)
    - case 2: source "HUD {count}", gold "HUD {count}" (warning-message)
    """
    import psycopg

    with psycopg.connect(fresh_db) as conn:
        cur = conn.execute(
            "INSERT INTO localization_projects (slug, name, source_locale, qps_threshold)"
            " VALUES ('test-proj', 'Test Project', 'en-US', 70) RETURNING id"
        )
        row = cur.fetchone()
        assert row is not None
        project_id = row[0]
        conn.execute(
            "INSERT INTO localization_glossary_terms (project_id, locale_code, source_term, target_term, notes)"
            " VALUES (%s, 'de-DE', 'HUD', 'HUD', ''), (%s, 'de-DE', 'Turn left', 'Links abbiegen', '')",
            (project_id, project_id),
        )
        conn.execute(
            "INSERT INTO localization_eval_golden_cases"
            " (project_id, locale_code, source_text, gold_translation, category, notes)"
            " VALUES (%s, 'de-DE', 'Turn left', 'Links abbiegen', 'short-label', ''),"
            "        (%s, 'de-DE', 'HUD {count}', 'HUD {count}', 'warning-message', '')",
            (project_id, project_id),
        )
        conn.commit()
    return fresh_db, project_id


@pytest.fixture
def db_client(seeded_project_id):
    """TestClient whose app pool points at the seeded test database (fake providers)."""
    import asyncio

    conninfo, _ = seeded_project_id
    settings = make_settings(database_url=conninfo)
    pool = db_module.create_pool(conninfo)
    asyncio.run(pool.open())
    asyncio.run(pool.wait())
    application = app.main.build_app(
        settings,
        pool=pool,
        chat_provider=FakeChatProvider(),
        embedding_provider=FakeEmbeddingProvider(),
    )
    client = TestClient(application)
    yield client
    asyncio.run(pool.close())
