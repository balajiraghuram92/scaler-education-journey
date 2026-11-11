"""P0 tests for the .NET connection-string converter in app/db.py."""

from app.db import dotnet_connstr_to_asyncpg_url


def test_standard_dotnet_format() -> None:
    url = dotnet_connstr_to_asyncpg_url(
        "Host=database;Port=5432;Database=studytracker;Username=studyuser;Password=secret"
    )
    assert url == "postgresql+asyncpg://studyuser:secret@database:5432/studytracker"


def test_defaults() -> None:
    url = dotnet_connstr_to_asyncpg_url("Host=localhost")
    assert url == "postgresql+asyncpg://studyuser@localhost:5432/studytracker"


def test_sql_server_aliases() -> None:
    url = dotnet_connstr_to_asyncpg_url(
        "Server=127.0.0.1;Database=StudyTracker;User Id=sa;Password=p@ss word"
    )
    assert url == "postgresql+asyncpg://sa:p%40ss%20word@127.0.0.1:5432/StudyTracker"
