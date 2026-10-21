# Async Persistence with SQLAlchemy 2.0 and Alembic

Most production incidents in async Python services trace back to the database layer: a request that fans out into 400 queries, an `expire_on_commit` surprise that raises `MissingGreenlet`, or a fleet whose combined connection pools exceed Postgres `max_connections` at the first deploy. Interviewers for backend and FDE roles use SQLAlchemy to test whether you understand sessions as units of work, not as connections, and whether you have actually run migrations against a live system.

## Concepts Covered

### Engine, sessionmaker and session-per-request

Three objects, three lifetimes. The **engine** (one per process) owns the connection pool and the dialect. The **`async_sessionmaker`** (one per process) is a factory holding session configuration. The **`AsyncSession`** (one per request or unit of work) holds an identity map, pending changes and, once used, one checked-out connection. A session is a transaction scope, not a connection: it borrows a connection from the pool on first use and returns it when the transaction ends.

```python
from collections.abc import AsyncIterator
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, MetaData, UniqueConstraint, func
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

NAMING = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING)


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", order_by="Message.id", lazy="raise"
    )


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (UniqueConstraint("conversation_id", "external_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[str]
    body: Mapped[str]
    conversation: Mapped[Conversation] = relationship(back_populates="messages", lazy="raise")


engine = create_async_engine(
    "postgresql+asyncpg://app:secret@db:5432/chat",
    pool_size=10, max_overflow=5, pool_timeout=10, pool_recycle=1800, pool_pre_ping=True,
)
SessionMaker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionMaker() as session:  # closing returns the connection to the pool
        yield session
```

In SQLAlchemy 2.0 you query with `select()` and execute it on the session: `await session.scalars(select(Conversation).where(...))` returns a `ScalarResult`, `await session.scalar(stmt)` returns the first column of the first row, and `await session.get(Conversation, 7)` is a primary-key lookup that consults the identity map first. The legacy `session.query()` API still exists but is not the style to show in an interview.

The session **autobegins**: the first `execute` starts a transaction, so calling `session.begin()` afterwards raises `InvalidRequestError: A transaction is already begun`. Pick one style per code path. `flush()` sends pending SQL (and assigns primary keys) inside the open transaction; `commit()` flushes and ends it.

### expire_on_commit and the MissingGreenlet trap

By default `commit()` expires every loaded attribute so the next access refetches fresh state. In sync code that is a hidden `SELECT`. In async code the refetch would be implicit I/O in a place where nothing can `await`, so you get `sqlalchemy.exc.MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here`. The same error appears when you touch an unloaded relationship (lazy loading) after the query returned, which is the classic crash when a serializer walks `conversation.messages`.

The remedies, in order of preference:

1. Load what you need up front with `selectinload` or `joinedload`.
2. Declare relationships `lazy="raise"` so a forgotten eager load fails loudly in tests with `InvalidRequestError` instead of intermittently in production.
3. Set `expire_on_commit=False` on the sessionmaker so objects stay readable after commit. The trade-off is that attributes can be stale, and server-generated values (defaults, triggers) are not reloaded, so call `await session.refresh(obj)` where you need them.
4. For the rare deliberate lazy load, use `await obj.awaitable_attrs.messages` (requires the `AsyncAttrs` mixin shown above) or `await session.run_sync(...)`.

> **Pitfall:** `lazy="selectin"` on the mapping silences the error by always paying for the extra query, even on endpoints that never read the collection. Prefer `lazy="raise"` plus explicit `options(...)` per query so every endpoint states its own loading plan.

### The N+1 problem and eager loading

N+1 means one query for the parents plus one more per parent to load a relationship. With 50 conversations it is 51 round trips, each paying network latency, so a 3 ms query becomes 150 ms before any serialization. This stdlib demo with `sqlite3` counts real statements for the three strategies (the same shapes SQLAlchemy emits for lazy loading, `selectinload` and `joinedload`):

```python
import sqlite3
from collections import defaultdict

conn = sqlite3.connect(":memory:")
conn.executescript("""
create table conversations (id integer primary key, user_id text);
create table messages (id integer primary key, conversation_id integer references conversations(id), body text);
""")
conn.executemany("insert into conversations(id,user_id) values (?,?)", [(i, "u1") for i in range(1, 51)])
conn.executemany("insert into messages(conversation_id, body) values (?,?)",
                 [(c, f"m{c}-{k}") for c in range(1, 51) for k in range(3)])

statements: list[str] = []
conn.set_trace_callback(statements.append)


def lazy_loading() -> int:
    convs = conn.execute("select id from conversations where user_id = ?", ("u1",)).fetchall()
    total = 0
    for (cid,) in convs:  # one query per conversation: the N in N+1
        total += len(conn.execute("select body from messages where conversation_id = ?", (cid,)).fetchall())
    return total


def selectin_style() -> int:
    ids = [r[0] for r in conn.execute("select id from conversations where user_id = ?", ("u1",))]
    marks = ",".join("?" * len(ids))
    by_conv = defaultdict(list)
    sql = f"select conversation_id, body from messages where conversation_id in ({marks})"
    for cid, body in conn.execute(sql, ids):
        by_conv[cid].append(body)
    return sum(len(v) for v in by_conv.values())


def joined_style() -> int:
    sql = ("select c.id, m.body from conversations c "
           "left join messages m on m.conversation_id = c.id where c.user_id = ?")
    return len(conn.execute(sql, ("u1",)).fetchall())


for fn in (lazy_loading, selectin_style, joined_style):
    statements.clear()
    result = fn()
    print(f"{fn.__name__:15} rows={result:4} queries={len(statements)}")
```

Output:

```text
lazy_loading    rows= 150 queries=51
selectin_style  rows= 150 queries=2
joined_style    rows= 150 queries=1
```

In SQLAlchemy the choice is per query. `selectinload(Conversation.messages)` issues the second `IN (...)` query (batched in chunks of 500 parent keys) and is the right default for collections: no row multiplication, and it composes with `LIMIT`. `joinedload` uses one `LEFT OUTER JOIN` and suits many-to-one or one-to-one relationships; for collections it multiplies parent rows and you must call `.unique()` on the result or SQLAlchemy raises.

```python
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload


async def recent_conversations(session: AsyncSession, user_id: str) -> list[Conversation]:
    stmt = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .options(selectinload(Conversation.messages))
        .order_by(Conversation.id.desc())
        .limit(50)
    )
    return list((await session.scalars(stmt)).all())


async def message_with_conversation(session: AsyncSession, message_id: int) -> Message | None:
    stmt = select(Message).where(Message.id == message_id).options(joinedload(Message.conversation))
    return (await session.scalars(stmt)).one_or_none()
```

### Transactions, savepoints and concurrency rules

Keep transaction boundaries in the application layer, one per business operation. `async with session.begin():` commits on success and rolls back on any exception. For partial failure inside a bulk operation use a **savepoint** with `begin_nested()`: a failed row rolls back to the savepoint while the outer transaction survives.

```python
from sqlalchemy.exc import IntegrityError


async def import_transcript(
    maker: async_sessionmaker[AsyncSession], user_id: str, items: list[tuple[str, str]]
) -> tuple[int, int]:
    saved = skipped = 0
    async with maker() as session, session.begin():
        conv = Conversation(user_id=user_id)
        session.add(conv)
        await session.flush()  # assigns conv.id inside the open transaction
        for external_id, body in items:
            try:
                async with session.begin_nested():  # SAVEPOINT
                    session.add(Message(conversation_id=conv.id, external_id=external_id, body=body))
                    await session.flush()
                saved += 1
            except IntegrityError:  # duplicate external_id: only this row is rolled back
                skipped += 1
    return saved, skipped
```

One hard rule: an `AsyncSession` is not safe for concurrent use. `asyncio.gather(session.execute(a), session.execute(b))` on one session fails with an error about concurrent operations (or interleaves state). To parallelise, open one session per task, each with its own connection. For queue-style claims use `select(Job).where(...).with_for_update(skip_locked=True)` so workers do not block each other.

### Connection pool sizing

The pool is per engine, and every worker process has its own engine. The budget that matters is global: `replicas × workers × (pool_size + max_overflow)` must stay below Postgres `max_connections` minus connections reserved for migrations, admin tools and other services.

| Setting | Meaning | Production default I use |
|---|---|---|
| `pool_size` | persistent connections | 5 to 10 per process |
| `max_overflow` | temporary extras under burst | about half of `pool_size` |
| `pool_timeout` | seconds to wait for a connection | 5 to 10, fail fast |
| `pool_pre_ping` | test connection on checkout | `True` behind load balancers |
| `pool_recycle` | max connection age in seconds | below the proxy idle timeout |

Three replicas of four workers at `10 + 5` is 180 possible connections against Postgres's default `max_connections` of 100, which surfaces under load as `asyncpg.exceptions.TooManyConnectionsError`. Fixes are smaller pools, fewer workers per replica, or PgBouncer. With PgBouncer in transaction pooling mode, asyncpg's prepared statements break, so pass `connect_args={"statement_cache_size": 0, "prepared_statement_cache_size": 0}`. If a task runner calls `asyncio.run` per job (Celery, for example), connections cannot be reused across event loops: use `NullPool` or build the engine inside the task.

### Alembic migrations and autogenerate pitfalls

`alembic init -t async migrations` generates an async `env.py`. The essential shape runs the synchronous migration context on an async connection via `run_sync`:

```python
import asyncio

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.db import Base, settings  # importing models registers every table on Base.metadata

target_metadata = Base.metadata


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(settings.database_url, poolclass=pool.NullPool)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


asyncio.run(run_migrations_online())
```

`alembic revision --autogenerate -m "add messages"` diffs the metadata against the live schema, and `alembic check` in CI fails when models and migrations drift. Autogenerate is a draft, never the final word:

- A renamed table or column appears as drop plus add, which destroys data. Rewrite it with `op.rename_table` or `op.alter_column(new_column_name=...)`.
- It does not see models that were never imported, so an empty migration usually means a missing import.
- Adding a `NOT NULL` column to a populated table fails unless you add it nullable, backfill, then alter, or supply a server default.
- Enum changes, check constraints and many server-default changes need hand-written operations.
- Constraint names are unstable without a `naming_convention`, so later migrations cannot reference them reliably.
- Index creation on a large Postgres table must be non-blocking: `with op.get_context().autocommit_block(): op.create_index(..., postgresql_concurrently=True)`.

> **Production note:** Run `alembic upgrade head` as a one-off job before rolling out new pods, never from every replica's startup. Use expand and contract: ship the additive migration first, deploy code that works with both schemas, then remove the old column in a later release.

## Practical Backend Scenario

Your support-chat product lists a customer's 50 latest conversations with their messages. After a feature launch p95 climbs from 120 ms to 2.1 s, and Postgres reports 3x more connections than the day before. Query logging shows 51 statements per request (N+1 from a serializer touching `conversation.messages`) and each request holds its connection while the serializer runs. The fix is a `selectinload` in the query, `lazy="raise"` to catch regressions in tests, a session scoped narrowly around the query rather than the whole response, and pool settings recalculated against the new replica count. A follow-up migration adds a composite index with `postgresql_concurrently=True`.

## Practice Loop

1. Define the two models above, create tables with Alembic (not `create_all`), and seed 50 conversations with 3 messages each.
2. Write the endpoint with a lazy relationship and capture the statement count with `echo=True` or a `before_cursor_execute` event listener. Then add `selectinload` and compare.
3. Trigger `MissingGreenlet` on purpose: commit, then read an attribute with `expire_on_commit=True`. Flip the setting and note what is now stale.
4. Set `lazy="raise"` on both relationships and confirm that forgetting `options(...)` fails in a test.
5. Run the savepoint import with a duplicate `external_id` and verify exactly one row is skipped.
6. Compute the connection budget for 3 replicas with 4 workers each, then open more sessions than the pool allows and observe `pool_timeout` fire.
7. Rename a column in the model, run `--autogenerate`, and rewrite the drop-plus-add into `alter_column(new_column_name=...)`.

## Evidence of Understanding

- I can explain why a session is a transaction scope and name the lifetimes of engine, sessionmaker and session.
- I can reproduce `MissingGreenlet` and fix it three ways, stating the cost of each.
- I can show an N+1 with a query count, remove it with `selectinload`, and explain when `joinedload` needs `.unique()`.
- I can explain why `begin()` fails after autobegin and when a savepoint is the right tool.
- I can compute a global connection budget and explain the PgBouncer and prepared-statement interaction.
- I can name five autogenerate blind spots and show how to ship an index without locking writes.

## Interview Questions to Rehearse

### Q: What is N+1 and how do you prevent it in async SQLAlchemy?
It is one query for parents plus one per parent for a relationship. In async it is worse because implicit lazy loading cannot even run, so it surfaces as `MissingGreenlet`. Use `selectinload` for collections, `joinedload` for many-to-one, make relationships `lazy="raise"` so regressions fail in tests, and assert on statement counts in a test for hot endpoints.

### Q: Why does accessing an attribute after commit raise MissingGreenlet?
`expire_on_commit=True` marks every attribute expired, so the next read tries to refresh with a blocking query outside an awaited call. Either configure `expire_on_commit=False` and refresh explicitly where server-generated values matter, or return plain DTOs built before the commit.

### Q: Can I `asyncio.gather` two queries on one AsyncSession?
No. A session holds one connection and one transaction state machine, and concurrent use is unsupported. Give each concurrent task its own session from the sessionmaker, or run the queries sequentially.

### Q: How do you size the pool?
Start from Postgres `max_connections`, subtract reserved headroom, divide across replicas and workers, then split into `pool_size` and `max_overflow`. Keep `pool_timeout` short so overload becomes fast failures instead of piling up requests. Behind PgBouncer use transaction pooling and disable asyncpg's prepared-statement caches.

### Q: What does Alembic autogenerate get wrong?
It reads only the metadata you imported, treats renames as drop and add, misses enum and check-constraint changes, and cannot backfill data. Always review the generated script, run `alembic check` in CI, and ship risky changes as expand-and-contract migrations.

## Common Pitfalls

- **Session in a global or `app.state`:** it will be shared across requests, mixing transactions. Store the sessionmaker, never a session.
- **Holding the session during slow external calls:** an LLM call inside an open transaction pins a connection for seconds. Query, close, call, then open a new unit of work.
- **Returning ORM objects from a closed session:** serialising after close hits detached or expired state. Build response models inside the unit of work.
- **`create_all` in production:** it never alters existing tables. Use migrations.
- **Mixing `session.begin()` with autobegin:** pick explicit `async with session.begin()` at the unit-of-work boundary.
- **Unbounded `selectinload` on a huge collection:** it loads every child row. Paginate the children separately.
- **Running migrations at app startup on every replica:** concurrent upgrades race. Use a single job or a lock.

## Suggested Extension

Write a pytest fixture that wraps each test in an outer transaction with `join_transaction_mode="create_savepoint"` on the session, so application-level `commit()` calls inside the code under test become savepoint releases and everything rolls back at test end. Add a query-counting listener on `before_cursor_execute` and fail any test where the hot endpoint exceeds three statements.
