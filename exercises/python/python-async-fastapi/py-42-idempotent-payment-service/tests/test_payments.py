import ast
import asyncio
from pathlib import Path

import pytest

import payments
from payments import DuplicateKey, GatewayError, Payment, PaymentInFlight, PaymentService


class State:
    """Shared bookkeeping across fakes."""

    def __init__(self):
        self.store: dict[str, Payment] = {}
        self.log: list[str] = []
        self.open_uows = 0


class FakeRepo:
    def __init__(self, store, staged):
        self._store, self._staged = store, staged

    async def get(self, key):
        return self._staged.get(key, self._store.get(key))

    async def add(self, payment):
        if payment.key in self._store or payment.key in self._staged:
            raise DuplicateKey(payment.key)
        self._staged[payment.key] = payment

    async def save(self, payment):
        self._staged[payment.key] = payment


class FakeUow:
    def __init__(self, state):
        self._state = state
        self._staged = {}
        self.payments = FakeRepo(state.store, self._staged)

    async def __aenter__(self):
        self._state.open_uows += 1
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._state.open_uows -= 1
        if self._staged:
            self._state.log.append("rollback")
        self._staged.clear()

    async def commit(self):
        self._state.store.update(self._staged)
        self._staged.clear()
        self._state.log.append("commit")


class FakeGateway:
    def __init__(self, state=None, delay=0.0, fail=False):
        self.state = state
        self.calls = 0
        self.delay, self.fail = delay, fail
        self.seen_open_uows = []
        self.seen_status = []
        self.args = []

    async def capture(self, tenant, amount_cents):
        self.calls += 1
        self.args.append((tenant, amount_cents))
        if self.state is not None:
            self.seen_open_uows.append(self.state.open_uows)
            self.seen_status.append(self.state.store.get("k5").status if "k5" in self.state.store else None)
        await asyncio.sleep(self.delay)
        if self.fail:
            raise GatewayError("declined")
        return f"ref-{self.calls}"


def make(gateway_factory=FakeGateway, **kwargs):
    state = State()
    gateway = gateway_factory(state=state, **kwargs)
    svc = PaymentService(lambda: FakeUow(state), gateway)
    return svc, gateway, state


@pytest.mark.asyncio
async def test_happy_path_and_idempotent_retry():
    svc, gw, state = make()
    first = await svc.charge("k1", "acme", 500)
    again = await svc.charge("k1", "acme", 500)
    assert first == again, "a retry must return the stored payment"
    assert first.status == "captured" and first.provider_ref == "ref-1"
    assert gw.calls == 1, "the gateway must be called once per key"
    assert state.store["k1"] == first
    assert gw.args == [("acme", 500)], "the gateway receives the tenant and amount"


@pytest.mark.asyncio
async def test_concurrent_duplicates_capture_once():
    svc, gw, state = make(delay=0.01)
    results = await asyncio.gather(*(svc.charge("k2", "acme", 100) for _ in range(10)), return_exceptions=True)
    assert gw.calls == 1, f"gateway was called {gw.calls} times for one key"
    assert sum(isinstance(r, Payment) for r in results) == 1
    assert sum(isinstance(r, PaymentInFlight) for r in results) == 9
    assert state.store["k2"].status == "captured"


@pytest.mark.asyncio
async def test_gateway_failure_is_recorded_and_terminal():
    svc, gw, state = make(fail=True)
    with pytest.raises(GatewayError):
        await svc.charge("k3", "acme", 100)
    assert state.store["k3"].status == "failed", "the failure must be recorded before re-raising"
    retry = await svc.charge("k3", "acme", 100)
    assert retry.status == "failed" and retry.provider_ref is None
    assert gw.calls == 1, "a failed payment is terminal: the retry must not call the gateway"


@pytest.mark.asyncio
async def test_invalid_amount_never_touches_ports():
    svc, gw, state = make()
    for bad in (0, -5):
        with pytest.raises(ValueError):
            await svc.charge("k4", "acme", bad)
    assert state.store == {} and state.log == [] and gw.calls == 0 and state.open_uows == 0


@pytest.mark.asyncio
async def test_no_transaction_is_open_during_the_gateway_call():
    svc, gw, state = make()
    await svc.charge("k5", "acme", 100)
    assert gw.seen_open_uows == [0], "the gateway must be called with no unit of work open"
    assert gw.seen_status == ["pending"], "the pending row must be committed before the gateway call"
    assert state.store["k5"].status == "captured"
    assert state.log == ["commit", "commit"], "one commit for the pending row, one for the final state"


@pytest.mark.asyncio
async def test_pending_payment_for_same_key_raises_in_flight():
    svc, gw, state = make()
    state.store["k6"] = Payment("k6", "acme", 100)  # another worker has reserved the key
    with pytest.raises(PaymentInFlight):
        await svc.charge("k6", "acme", 100)
    assert gw.calls == 0, "an in-flight payment must not be charged again"
    assert state.store["k6"].status == "pending"


@pytest.mark.asyncio
async def test_replay_of_finished_payment_is_returned_unchanged():
    svc, gw, state = make()
    done = Payment("k7", "acme", 100, status="captured", provider_ref="ref-old")
    state.store["k7"] = done
    assert await svc.charge("k7", "acme", 100) == done, "a finished payment is replayed unchanged"
    assert gw.calls == 0 and state.store["k7"] == done


@pytest.mark.asyncio
async def test_different_keys_are_independent():
    svc, gw, state = make()
    a = await svc.charge("ka", "acme", 100)
    b = await svc.charge("kb", "globex", 250)
    assert (a.provider_ref, b.provider_ref) == ("ref-1", "ref-2")
    assert gw.calls == 2 and set(state.store) == {"ka", "kb"}


def test_service_module_imports_no_persistence_or_framework():
    tree = ast.parse(Path(payments.__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    forbidden = {"sqlalchemy", "fastapi", "starlette", "sqlite3", "aiosqlite", "asyncpg", "psycopg", "pydantic", "httpx"}
    assert not (imported & forbidden), f"the service layer must stay framework-free, found {sorted(imported & forbidden)}"
