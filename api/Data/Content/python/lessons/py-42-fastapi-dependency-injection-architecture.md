# Dependency Injection and Service Architecture in FastAPI

Every FastAPI service that survives its second year has solved the same problem: where do database sessions, HTTP clients, settings and business rules live, and how do you swap them in a test? `Depends` is the framework's answer, but it is only a wiring mechanism. Interviewers use it to probe whether you understand lifetimes (per call, per request, per process), cleanup ordering, and whether your route handlers are thin adapters or a 200-line tangle of SQL and HTTP calls.

## Concepts Covered

### How Depends resolves and caches

When a request arrives, FastAPI inspects the path operation signature and builds a dependency tree. Each parameter whose default (or `Annotated` metadata) is `Depends(callable)` becomes a node. The callable's own parameters are inspected recursively, so sub-dependencies, query parameters, headers and the body are all collected from one declarative signature. Nodes are resolved depth first, and each resolved value is stored in a per-request cache keyed by the callable (plus any security scopes). If three sub-dependencies all depend on `get_settings`, it runs once for that request. `Depends(dep, use_cache=False)` opts out and calls it again.

Three lifetimes matter and candidates routinely blur them:

| Lifetime | Mechanism | Typical resource |
|---|---|---|
| Per process | `lifespan`, `app.state`, `lru_cache` | engine, connection pool, `httpx.AsyncClient`, settings |
| Per request | `Depends` with caching, `yield` dependencies | `AsyncSession`, current user, request context |
| Per call | plain constructor call inside a dependency | service objects that are cheap to build |

The request cache does not span requests. A dependency that builds an expensive object is rebuilt on every request unless the object itself lives in the per-process tier. Also remember the execution model: an `async def` dependency runs on the event loop, while a plain `def` dependency is pushed to the AnyIO threadpool (40 worker threads by default). A synchronous dependency that does blocking I/O is fine for throughput, but one that touches an `async` client from a thread is a bug.

### Annotated, class-based, and parametrized dependencies

Since FastAPI 0.95 the preferred spelling is `Annotated`, which lets you name a dependency once and reuse the alias everywhere. The signature stays honest to type checkers and the default-value slot stays free.

```python
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    maker: async_sessionmaker[AsyncSession] = request.app.state.session_maker
    async with maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Pagination:
    def __init__(
        self,
        limit: Annotated[int, Query(ge=1, le=200)] = 50,
        offset: Annotated[int, Query(ge=0)] = 0,
    ) -> None:
        self.limit = limit
        self.offset = offset


PageDep = Annotated[Pagination, Depends()]  # class is the callable; params come from __init__


class RequireRole:
    """Parametrized dependency: the instance is the callable (via __call__)."""

    def __init__(self, role: str) -> None:
        self.role = role

    async def __call__(self, current_user: "CurrentUserDep") -> "User":
        if self.role not in current_user.roles:
            raise HTTPException(status_code=403, detail="insufficient role")
        return current_user


# Each RequireRole("admin") instance is a distinct cache key.
# @router.delete("/rides/{ride_id}", dependencies=[Depends(RequireRole("admin"))])
```

A class used as a dependency is simply a callable; FastAPI introspects `__init__`. Passing `Depends()` with no argument tells FastAPI to use the annotated type. The `__call__` pattern gives you configurable dependencies (roles, rate-limit buckets, feature flags) without closures.

### yield dependencies and cleanup

A dependency that `yield`s is wrapped as a context manager on a per-request `AsyncExitStack`. Code before `yield` is setup, the yielded value is injected, and code after runs at teardown, in reverse order of setup. An exception raised by the handler is thrown into the generator at the `yield`, so `try/except/finally` around it works exactly like a `with` block. This stdlib model is what FastAPI does for you:

```python
import asyncio
from contextlib import AsyncExitStack, asynccontextmanager


@asynccontextmanager
async def get_pool():
    print("pool: open")
    try:
        yield "pool"
    finally:
        print("pool: close")


@asynccontextmanager
async def get_session():
    print("session: begin")
    try:
        yield "session"
        print("session: commit")
    except Exception as exc:
        print(f"session: rollback ({type(exc).__name__})")
        raise
    finally:
        print("session: close")


async def handle(fail: bool) -> None:
    async with AsyncExitStack() as stack:
        pool = await stack.enter_async_context(get_pool())
        session = await stack.enter_async_context(get_session())
        print("handler runs with", pool, session)
        if fail:
            raise ValueError("boom")


async def main() -> None:
    await handle(False)
    print("---")
    try:
        await handle(True)
    except ValueError:
        print("error propagated")


asyncio.run(main())
```

Running this prints `pool: open`, `session: begin`, the handler line, `session: commit`, `session: close`, `pool: close` for the happy path. On failure the commit line is replaced by `session: rollback (ValueError)`, the close lines still run in reverse order, and the error propagates.

> **Pitfall:** Do not put the commit in the post-`yield` code. The timing of teardown relative to the response has changed between releases: 0.106 moved it before the response was sent, and 0.118 moved it back to after the response (to support streaming responses). On a current release (checked on 0.154) a plain yield dependency tears down after the response has gone out, so a client can already hold a `200` when your commit fails. `Depends(dep, scope="function")` ends the dependency right after the path function and before the response is sent, but explicit is still better: commit inside the service (a unit of work) and let the dependency only open and close the session. Check the "Dependencies with yield" page for your pinned version.

Two related traps. A yielded `AsyncSession` must not be handed to a `BackgroundTasks` function, because it may be closed by the time the task runs; give the task its own session from the sessionmaker. And an exception after `yield` that you catch and swallow turns a failed request into a silent success, so re-raise.

### lifespan for process-wide resources

`@app.on_event("startup")` is deprecated. The `lifespan` async context manager owns everything that should exist exactly once per worker process: the engine and its pool, the shared `httpx.AsyncClient` for your LLM provider, a Redis client, loaded model weights. Creating an `AsyncClient` per request throws away connection reuse and TLS handshakes and shows up as latency and ephemeral-port exhaustion under load.

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    engine = create_async_engine(
        settings.database_url, pool_size=10, max_overflow=5, pool_pre_ping=True
    )
    app.state.engine = engine
    app.state.session_maker = async_sessionmaker(engine, expire_on_commit=False)
    app.state.llm_http = httpx.AsyncClient(
        base_url=settings.llm_base_url,
        timeout=httpx.Timeout(settings.llm_timeout_s, connect=3.0),
        limits=httpx.Limits(max_connections=50),
    )
    try:
        yield
    finally:
        await app.state.llm_http.aclose()
        await engine.dispose()


app = FastAPI(lifespan=lifespan)
```

Lifespan runs once per worker process, so four uvicorn workers means four pools. It does not run under `TestClient(app)` unless you use it as a context manager (`with TestClient(app) as client:`), and `httpx.ASGITransport` does not run it at all. That single fact explains most "works in prod, `AttributeError: state` in tests" reports.

### Layered architecture with Protocol ports

The router should translate HTTP into a method call and back. The service holds business rules and depends on abstractions (ports) declared as `typing.Protocol`, so any object with matching methods satisfies them structurally, with no inheritance and no import of the SQLAlchemy implementation. The repository adapter is the only layer that knows about tables.

```python
from __future__ import annotations

import asyncio
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class Fare:
    ride_id: str
    amount: Decimal


class FareRepository(Protocol):
    async def save(self, fare: Fare) -> None: ...
    async def get(self, ride_id: str) -> Fare | None: ...


class SurgePricer(Protocol):
    def multiplier(self, zone: str) -> Decimal: ...


class FareService:
    def __init__(self, repo: FareRepository, pricer: SurgePricer) -> None:
        self._repo = repo
        self._pricer = pricer

    async def quote(self, ride_id: str, zone: str, base: Decimal) -> Fare:
        if (existing := await self._repo.get(ride_id)) is not None:
            return existing  # idempotent: a retry returns the first quote
        amount = (base * self._pricer.multiplier(zone)).quantize(Decimal("0.01"))
        fare = Fare(ride_id, amount)
        await self._repo.save(fare)
        return fare


class InMemoryFareRepo:
    def __init__(self) -> None:
        self.rows: dict[str, Fare] = {}
        self.saves = 0

    async def save(self, fare: Fare) -> None:
        self.saves += 1
        self.rows[fare.ride_id] = fare

    async def get(self, ride_id: str) -> Fare | None:
        return self.rows.get(ride_id)


class FixedSurge:
    def multiplier(self, zone: str) -> Decimal:
        return Decimal("1.5") if zone == "airport" else Decimal("1.0")


async def main() -> None:
    repo = InMemoryFareRepo()
    svc = FareService(repo, FixedSurge())
    print(await svc.quote("r1", "airport", Decimal("20.00")))
    print(await svc.quote("r1", "downtown", Decimal("20.00")))
    print(repo.saves)


asyncio.run(main())
```

The output is `Fare(ride_id='r1', amount=Decimal('30.00'))` twice, then `1`: the retry returned the stored quote and the repository was written once. Notice what the test needed: no database, no event loop trickery, no patching. The FastAPI side is then a dependency factory: `def get_fare_service(session: SessionDep, pricer: PricerDep) -> FareService: return FareService(SqlFareRepo(session), pricer)`. Keep the wiring in one module (the composition root) and let routers depend only on `get_fare_service`.

> **Interview tip:** Say that you use `Protocol` for ports because the service package must not import the persistence package. A reviewer who sees `from app.db import models` inside `services/` knows the layering is decorative.

### Configuration with pydantic-settings

Settings are a dependency like any other: validated at startup, immutable in use, overridable in tests. `pydantic-settings` (a separate package since Pydantic v2) reads environment variables, a dotenv file and a secrets directory, with init arguments taking highest precedence.

```python
from functools import lru_cache
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_", env_file=".env", extra="ignore", env_nested_delimiter="__"
    )

    environment: Literal["local", "staging", "prod"] = "local"
    database_url: str
    llm_base_url: str = "https://api.example-llm.com/v1"
    llm_api_key: SecretStr
    llm_timeout_s: float = 30.0


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]  # required fields come from the environment
```

`SecretStr` keeps the key out of `repr` and logs; call `.get_secret_value()` only at the point of use. `extra="ignore"` matters because a shared `.env` file with unrelated keys otherwise fails validation. Missing required values fail at import or first call, which is the point: crash on boot, not on the first request at 3 a.m. `lru_cache` makes the settings a process singleton while `Depends(get_settings)` keeps it overridable.

### Testing with dependency_overrides

`app.dependency_overrides` maps the original callable to a replacement. The replacement may declare its own parameters, which FastAPI resolves normally, and the override applies at any depth of the tree.

```python
from collections.abc import Iterator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> Iterator[TestClient]:
    app = create_app()  # factory: no import-time side effects
    repo = InMemoryFareRepo()
    app.dependency_overrides[get_fare_service] = lambda: FareService(repo, FixedSurge())
    with TestClient(app) as c:  # context manager runs lifespan
        yield c
    app.dependency_overrides.clear()


def test_quote_is_idempotent(client: TestClient) -> None:
    body = {"zone": "airport", "base": "20.00"}
    first = client.post("/rides/r1/quote", json=body).json()
    second = client.post("/rides/r1/quote", json={**body, "zone": "downtown"}).json()
    assert first == second
```

Override at the seam closest to the side effect (the service or the port), not deep inside, so the test still exercises routing, validation and serialization. An application factory (`create_app`) beats a module-level `app` because overrides and settings never leak between tests.

## Practical Backend Scenario

You own an LLM gateway: clients POST a prompt, the service checks the tenant's token budget in Postgres, calls a provider through a shared `httpx.AsyncClient`, and records usage. Provider calls are slow and flaky, so latency tests need a fake provider that sleeps and fails on demand. Because the provider client lives in `lifespan` and is exposed through a `get_provider` dependency typed as a `Protocol`, the test swaps in a fake in one line, asserts the budget is debited exactly once on a retried request, and never opens a socket. The same layout lets you add a second provider for failover by writing a class that satisfies the same port, with no change to routers or service tests.

## Practice Loop

1. Write three dependencies: `get_settings` (cached), `get_current_tenant` (depends on settings) and `get_budget_guard` (depends on both). Add a `print` to `get_settings` and confirm it runs once per request, then switch to `use_cache=False` and observe the difference.
2. Add a `yield` dependency that prints setup and teardown. Raise an exception in the handler and confirm the teardown sees it. Then add a second `yield` dependency and verify the teardown order is reversed.
3. Move an engine and an `httpx.AsyncClient` into `lifespan`. Run `uvicorn --workers 2` and count how many pools are created.
4. Define `UsageRepository` and `Provider` as Protocols, implement in-memory fakes, and write a service-level test with no FastAPI import at all.
5. Write one route-level test using `dependency_overrides` and `with TestClient(app)`. Then remove the `with` and observe the lifespan-related failure.
6. Replace hard-coded config with a `Settings` class, test that a missing `APP_DATABASE_URL` fails at startup, and confirm `repr(settings)` hides the API key.

## Evidence of Understanding

- I can state the cache key of a dependency and predict, for a given tree, how many times each callable runs per request.
- I can explain why a sync `def` dependency and an `async def` dependency execute in different places.
- I can show the teardown order of two `yield` dependencies and explain what happens when the handler raises.
- I can justify why commit lives in the service rather than in post-`yield` code.
- I can say which resources belong in `lifespan` and why `TestClient` needs the context manager to run it.
- I can test a service with Protocol fakes without importing FastAPI or SQLAlchemy.

## Interview Questions to Rehearse

### Q: A dependency is used by three sub-dependencies of one endpoint. How many times does it run, and how do you change that?
Once per request: FastAPI caches the resolved value by callable (and security scopes) for the lifetime of that request. `Depends(dep, use_cache=False)` forces re-execution at that injection point. The cache never survives the request, so process-wide singletons belong in `lifespan` or `lru_cache`.

### Q: Why is a per-request `httpx.AsyncClient` a production bug?
Each client owns its own connection pool, so every request pays DNS, TCP and TLS setup and discards keep-alive connections. Under load this inflates latency and can exhaust ephemeral ports or the provider's rate limits. Create one client in `lifespan`, bound timeouts and pool limits explicitly, and close it on shutdown.

### Q: Where should the database commit happen and why?
In a service-level unit of work, inside the request handling path. Teardown code after a `yield` runs at a version-dependent moment relative to the response, so a failed commit there can arrive after the client has already received success. The dependency's job is only to open and close the session.

### Q: How do you test an endpoint without the real database or LLM provider?
Build the app with a factory, then set `app.dependency_overrides[get_service] = lambda: Service(fake_repo, fake_provider)`. Because services depend on `Protocol` ports, fakes need no patching. Use `with TestClient(app)` when the test needs lifespan, and clear overrides afterwards.

### Q: Why Protocol instead of an abstract base class for ports?
Protocols are structural, so adapters and fakes satisfy them without importing the port module or inheriting from it. That keeps the dependency arrow pointing from adapter to domain, makes third-party objects usable as ports, and lets type checkers verify wiring statically.

## Common Pitfalls

- **Import-time side effects:** building the engine or reading settings at module import makes tests and tooling (Alembic, OpenAPI generation) fail without a database. Defer to `lifespan` and factories.
- **Global singletons hidden behind `Depends`:** a module-level `session = AsyncSession(engine)` shared by all requests corrupts transactions under concurrency. A session is per request, never per process.
- **Business logic in routers:** if a route imports SQLAlchemy models and `httpx`, it cannot be tested without both.
- **Forgetting `use_cache` implications:** a dependency with side effects (such as generating a request ID) that is expected to run twice will silently run once.
- **Overrides that leak:** forgetting `dependency_overrides.clear()` makes tests order-dependent.
- **Using `lru_cache` on a dependency that takes request data:** the first caller's value is served to everyone.
- **Blocking work in an `async def` dependency:** it stalls the event loop for all requests; use `def` (threadpool) or an async driver.

## Suggested Extension

Add a second `Provider` implementation (for example a regional fallback) and a `FailoverProvider` that wraps a list of providers behind the same `Provider` Protocol, with a circuit breaker. Wire it in the composition root, then prove with Protocol fakes that the service and the routers did not change.
