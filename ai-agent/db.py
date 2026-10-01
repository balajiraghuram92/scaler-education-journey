"""Async connection pool for the app.

The pool tolerates a database where the ``vector`` extension does not exist
yet (brand-new DB before migrate.py has run): the pgvector type adapters are
registered only when the type is present. Connections opened before the
extension existed are recycled by ``max_lifetime``; restart the service after
the first migration for immediate effect.
"""

import logging

import psycopg
from pgvector.psycopg import register_vector_async
from psycopg import pq
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)


async def configure_connection(conn: psycopg.AsyncConnection) -> None:
    try:
        await register_vector_async(conn)
    except psycopg.ProgrammingError:
        # "vector type not found in the database": run migrate.py first.
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
