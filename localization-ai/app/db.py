"""Async connection pool plus the small read helpers the service needs.

The schema is owned by the .NET EF Core migrations: this service creates no
tables. Table and column names below match the LA1 entity/Fluent definitions
(``localization_*`` tables, snake_case columns).

The pool tolerates a database where the ``vector`` extension does not exist
yet: the pgvector type adapters are registered only when the type is present.
"""

import logging
from dataclasses import dataclass

import psycopg
from fastapi import Request
from pgvector.psycopg import register_vector_async
from psycopg import pq
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProjectRow:
    id: int
    slug: str
    qps_threshold: int


@dataclass(frozen=True)
class GlossaryTermRow:
    locale_code: str
    source_term: str
    target_term: str


@dataclass(frozen=True)
class GoldenCaseRow:
    id: int
    locale_code: str
    source_text: str
    gold_translation: str
    category: str
    notes: str | None


async def configure_connection(conn: psycopg.AsyncConnection) -> None:
    try:
        await register_vector_async(conn)
    except psycopg.ProgrammingError:
        # "vector type not found in the database": the LA1 migration that
        # creates the extension has not been applied yet.
        logger.warning("pgvector type not found; vector adapters not registered on this connection")
    # The pool requires an idle connection after configure.
    if conn.info.transaction_status != pq.TransactionStatus.IDLE:
        await conn.rollback()


def create_pool(conninfo: str) -> AsyncConnectionPool:
    return AsyncConnectionPool(
        conninfo=conninfo,
        configure=configure_connection,
        min_size=1,
        max_size=5,
        max_lifetime=3600,
        open=False,
    )


def pool_from_request(request: Request) -> AsyncConnectionPool:
    return request.app.state.pool


async def fetch_project(conn: psycopg.AsyncConnection, slug: str) -> ProjectRow | None:
    cur = await conn.execute(
        "SELECT id, slug, qps_threshold FROM localization_projects WHERE slug = %s",
        (slug,),
    )
    row = await cur.fetchone()
    if row is None:
        return None
    return ProjectRow(id=row[0], slug=row[1], qps_threshold=row[2])


async def fetch_glossary_terms(conn: psycopg.AsyncConnection, project_id: int) -> list[GlossaryTermRow]:
    cur = await conn.execute(
        "SELECT locale_code, source_term, target_term"
        " FROM localization_glossary_terms WHERE project_id = %s ORDER BY id",
        (project_id,),
    )
    return [GlossaryTermRow(locale_code=r[0], source_term=r[1], target_term=r[2]) for r in await cur.fetchall()]


async def fetch_golden_cases(conn: psycopg.AsyncConnection, project_id: int) -> list[GoldenCaseRow]:
    cur = await conn.execute(
        "SELECT id, locale_code, source_text, gold_translation, category, notes"
        " FROM localization_eval_golden_cases WHERE project_id = %s ORDER BY id",
        (project_id,),
    )
    return [
        GoldenCaseRow(id=r[0], locale_code=r[1], source_text=r[2], gold_translation=r[3], category=r[4], notes=r[5])
        for r in await cur.fetchall()
    ]
