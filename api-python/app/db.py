"""Ported from the StudyTrackerContext wiring in api/Program.cs (lines 25-53).

Async engine plus a per-request session dependency. Includes one small tested
function converting a .NET-style connection string to an asyncpg URL.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from urllib.parse import quote_plus

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .settings import get_dotnet_connection_string, get_environment


def dotnet_connstr_to_asyncpg_url(connstr: str) -> str:
    """Convert `Host=..;Port=..;Database=..;Username=..;Password=..` to an asyncpg URL.

    Accepts SQL-Server-style aliases seen in appsettings.Development.json
    (Server, Database, User Id, Password) as well.
    """
    parts: dict[str, str] = {}
    for chunk in connstr.split(";"):
        chunk = chunk.strip()
        if not chunk or "=" not in chunk:
            continue
        key, _, value = chunk.partition("=")
        parts[key.strip().lower()] = value.strip()
    host = parts.get("host", parts.get("server", "localhost"))
    port = parts.get("port", "5432")
    database = parts.get("database", parts.get("initial catalog", "studytracker"))
    username = parts.get("username", parts.get("user id", parts.get("user", "studyuser")))
    password = parts.get("password", "")
    auth = quote_plus(username)
    if password:
        auth += f":{quote_plus(password)}"
    return f"postgresql+asyncpg://{auth}@{host}:{port}/{database}"


def get_asyncpg_url() -> str:
    return dotnet_connstr_to_asyncpg_url(
        get_dotnet_connection_string(get_environment())
    )


_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine():  # type: ignore[no-untyped-def]
    global _engine
    if _engine is None:
        _engine = create_async_engine(get_asyncpg_url(), pool_pre_ping=True)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    factory = get_session_factory()
    async with factory() as session:
        yield session
