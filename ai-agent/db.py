import config
from psycopg_pool import AsyncConnectionPool
from pgvector.psycopg import register_vector_async

async def configure_connection(conn):
    await register_vector_async(conn)


pool = AsyncConnectionPool(
    conninfo=config.DATABASE_URL,
    configure=configure_connection,
    min_size=1,
    max_size=5,
    open=False
)