import os
import shutil
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import jwt
import pytest
from fastapi.testclient import TestClient

AGENT_DIR = Path(__file__).resolve().parent.parent
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

import config  # noqa: E402
import main  # noqa: E402

TEST_KEY = "unit-test-signing-key-0123456789abcdef"  # 38 bytes, test only
PGVECTOR_IMAGE = os.environ.get("AI_AGENT_TEST_PG_IMAGE", "pgvector/pgvector:pg16")


def make_settings(**overrides) -> config.Settings:
    values = dict(
        jwt_signing_key=TEST_KEY,
        muse_api_key="unit-test-muse-key",
        # Nothing listens on port 1; the pool is never opened in unit tests.
        database_conninfo="host=127.0.0.1 port=1 dbname=none user=none",
    )
    values.update(overrides)
    return config.Settings(**values)


def make_token(key: str = TEST_KEY, **claims) -> str:
    now = datetime.now(UTC)
    payload = {
        "nameid": "42",
        "email": "learner@example.test",
        "role": "Learner",
        "iss": "neuralascent",
        "aud": "neuralascent-app",
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=10),
    }
    payload.update(claims)
    payload = {k: v for k, v in payload.items() if v is not None}  # None = omit claim
    return jwt.encode(payload, key, algorithm="HS256")


def bearer(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def settings() -> config.Settings:
    return make_settings()


@pytest.fixture
def app(settings):
    return main.build_app(settings)


@pytest.fixture
def client(app):
    # No `with`: lifespan (pool open, tracing) is not started in unit tests.
    return TestClient(app)


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
        pytest.skip(f"migration/DB tests need Docker: {reason}")
    name = f"ai-agent-test-pg-{uuid.uuid4().hex[:8]}"
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
    """A brand-new empty database (no vector extension) plus a stub `lessons` table,
    standing in for the API's EF Core schema that migration 002 references."""
    import psycopg
    from psycopg.conninfo import make_conninfo

    dbname = "t_" + uuid.uuid4().hex[:10]
    with psycopg.connect(dbname="postgres", autocommit=True, **pg_server) as admin:
        admin.execute(f'CREATE DATABASE "{dbname}"')
    conninfo = make_conninfo(dbname=dbname, **pg_server)
    yield conninfo
    with psycopg.connect(dbname="postgres", autocommit=True, **pg_server) as admin:
        admin.execute(f'DROP DATABASE IF EXISTS "{dbname}" WITH (FORCE)')


def create_lessons_stub(conninfo: str) -> None:
    import psycopg

    with psycopg.connect(conninfo, autocommit=True) as conn:
        conn.execute("CREATE TABLE lessons (id INT PRIMARY KEY)")
