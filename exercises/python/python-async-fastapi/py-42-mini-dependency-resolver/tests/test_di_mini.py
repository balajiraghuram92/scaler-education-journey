import pytest

from di_mini import CircularDependencyError, Depends, Resolver


@pytest.mark.asyncio
async def test_cache_is_shared_and_use_cache_false_opts_out():
    calls = []

    def settings():
        calls.append("settings")
        return {"env": "test"}

    def a(s=Depends(settings)):
        return s

    def b(s=Depends(settings, use_cache=False)):
        return s

    async def endpoint(x=Depends(a), y=Depends(b), z=Depends(settings)):
        return (x, y, z)

    x, y, z = await Resolver().run(endpoint)
    assert calls == ["settings", "settings"], "cached once for a and z, called again for the use_cache=False edge"
    assert x is z, "cached dependants must share the same object"


@pytest.mark.asyncio
async def test_cache_lives_for_one_run_only():
    calls = []

    def counter():
        calls.append(1)
        return len(calls)

    async def endpoint(n=Depends(counter)):
        return n

    resolver = Resolver()
    assert await resolver.run(endpoint) == 1
    assert await resolver.run(endpoint) == 2, "a new run must not reuse the previous run's cache"


@pytest.mark.asyncio
async def test_generator_dependencies_are_torn_down_in_reverse_order():
    log = []

    async def pool():
        log.append("pool+")
        try:
            yield "pool"
        finally:
            log.append("pool-")

    async def session(p=Depends(pool)):
        log.append("session+")
        try:
            yield f"session({p})"
        finally:
            log.append("session-")

    async def endpoint(s=Depends(session)):
        log.append("handler")
        return s

    assert await Resolver().run(endpoint) == "session(pool)"
    assert log == ["pool+", "session+", "handler", "session-", "pool-"], "teardown must be the reverse of setup"


@pytest.mark.asyncio
async def test_endpoint_exception_is_thrown_into_generators():
    log = []

    async def pool():
        log.append("pool+")
        try:
            yield "pool"
        finally:
            log.append("pool-")

    async def session(p=Depends(pool)):
        log.append("session+")
        try:
            yield "session"
        except ValueError:
            log.append("rollback")
            raise
        finally:
            log.append("session-")

    async def endpoint(s=Depends(session)):
        log.append("handler")
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        await Resolver().run(endpoint)
    assert log == ["pool+", "session+", "handler", "rollback", "session-", "pool-"]


@pytest.mark.asyncio
async def test_overrides_and_runtime_values():
    def get_repo():
        return "real"

    async def service(repo=Depends(get_repo)):
        return repo.upper()

    async def endpoint(svc=Depends(service), ride_id: str = "r0"):
        return (svc, ride_id)

    assert await Resolver().run(endpoint, ride_id="r9") == ("REAL", "r9")
    assert await Resolver({get_repo: lambda: "fake"}).run(endpoint) == ("FAKE", "r0")


@pytest.mark.asyncio
async def test_override_keeps_original_cache_key_and_resolves_its_own_dependencies():
    calls = []

    def config():
        return "cfg"

    def real_db():
        calls.append("real")
        return "real-db"

    def fake_db(cfg=Depends(config)):
        calls.append("fake")
        return f"fake-db({cfg})"

    def repo(db=Depends(real_db)):
        return db

    def audit(db=Depends(real_db)):
        return db

    async def endpoint(r=Depends(repo), a=Depends(audit)):
        return (r, a)

    result = await Resolver({real_db: fake_db}).run(endpoint)
    assert result == ("fake-db(cfg)", "fake-db(cfg)"), "the replacement's own Depends parameters must be resolved"
    assert calls == ["fake"], "cache is keyed by the original callable, so the override runs once"


@pytest.mark.asyncio
async def test_sync_async_and_nested_dependencies_and_sync_endpoint():
    def sync_dep():
        return 1

    async def async_dep(a=Depends(sync_dep)):
        return a + 1

    async def gen_dep(b=Depends(async_dep)):
        yield b + 1

    def endpoint(c=Depends(gen_dep)):  # a plain def endpoint is allowed
        return c + 1

    assert await Resolver().run(endpoint) == 4


@pytest.mark.asyncio
async def test_cycles_are_reported_with_the_chain():
    def a(x=None):
        return x

    def b(y=Depends(a)):
        return y

    a.__defaults__ = (Depends(b),)

    def endpoint(v=Depends(a)):
        return v

    with pytest.raises(CircularDependencyError, match="a -> b -> a"):
        await Resolver().run(endpoint)

    def selfish(x=None):
        return x

    selfish.__defaults__ = (Depends(selfish),)

    def endpoint2(v=Depends(selfish)):
        return v

    with pytest.raises(CircularDependencyError, match="selfish -> selfish"):
        await Resolver().run(endpoint2)


@pytest.mark.asyncio
async def test_missing_value_raises_type_error_and_defaults_are_used():
    def endpoint(ride_id: str):
        return ride_id

    with pytest.raises(TypeError, match="ride_id"):
        await Resolver().run(endpoint)

    def with_default(ride_id: str = "fallback"):
        return ride_id

    assert await Resolver().run(with_default) == "fallback"
    assert await Resolver().run(with_default, ride_id="given") == "given"
