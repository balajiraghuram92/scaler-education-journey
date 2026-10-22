import random
import threading

import pytest

from budget.guard import BudgetExceededError, BudgetGuard, RescanGuard, UnknownCallError

CAPS = {"tokens": 100, "calls": 5}


def test_charge_and_refund_update_usage():
    guard = BudgetGuard(CAPS)
    first = guard.charge("acme", {"tokens": 60, "calls": 1})
    assert guard.used("acme", "tokens") == 60
    assert guard.used("acme", "calls") == 1
    guard.refund(first)
    assert guard.used("acme", "tokens") == 0 and guard.used("acme", "calls") == 0


def test_charge_returns_distinct_call_ids():
    guard = BudgetGuard(CAPS)
    ids = {guard.charge("acme", {"tokens": 1}) for _ in range(5)}
    assert len(ids) == 5


def test_a_rejected_charge_changes_nothing_in_any_limit():
    guard = BudgetGuard(CAPS)
    guard.charge("acme", {"tokens": 90, "calls": 1})
    with pytest.raises(BudgetExceededError):
        guard.charge("acme", {"tokens": 20, "calls": 1})  # tokens exceed, calls would fit
    assert guard.used("acme", "tokens") == 90
    assert guard.used("acme", "calls") == 1, "validate first, mutate last: calls must not have moved"


def test_cap_boundary_is_inclusive():
    guard = BudgetGuard(CAPS)
    guard.charge("acme", {"tokens": 100})
    assert guard.used("acme", "tokens") == 100
    with pytest.raises(BudgetExceededError):
        guard.charge("acme", {"tokens": 1})
    guard.charge("acme", {"tokens": 0})  # zero usage is always fine


def test_invalid_usage_raises_value_error():
    guard = BudgetGuard(CAPS)
    with pytest.raises(ValueError):
        guard.charge("acme", {"tokens": -1})
    with pytest.raises(ValueError):
        guard.charge("acme", {"gpus": 1})
    with pytest.raises(ValueError):
        guard.charge("acme", {"tokens": 5, "gpus": 1})
    assert guard.used("acme", "tokens") == 0, "a rejected charge must not leak partial usage"


def test_tenants_are_isolated():
    guard = BudgetGuard(CAPS)
    guard.charge("acme", {"tokens": 100})
    guard.charge("globex", {"tokens": 100})  # globex has its own budget
    assert guard.used("acme", "tokens") == 100 and guard.used("globex", "tokens") == 100
    assert guard.used("nobody", "tokens") == 0


def test_refund_is_single_use():
    guard = BudgetGuard(CAPS)
    call = guard.charge("acme", {"tokens": 10})
    guard.refund(call)
    with pytest.raises(UnknownCallError):
        guard.refund(call)
    with pytest.raises(UnknownCallError):
        guard.refund(9999)
    assert guard.used("acme", "tokens") == 0


def test_budget_exceeded_error_carries_tenant_and_limit():
    guard = BudgetGuard(CAPS)
    with pytest.raises(BudgetExceededError) as info:
        guard.charge("acme", {"tokens": 101})
    assert info.value.tenant == "acme" and info.value.limit == "tokens"


def test_fast_guard_agrees_with_rescan_oracle_on_random_operations():
    rng = random.Random(11)
    for _ in range(100):
        fast, slow = BudgetGuard(CAPS), RescanGuard(CAPS)
        live = []
        for _ in range(40):
            if live and rng.random() < 0.3:
                fast_id, slow_id = live.pop(rng.randrange(len(live)))
                fast.refund(fast_id)
                slow.refund(slow_id)
            else:
                tenant = rng.choice(["a", "b"])
                usage = {"tokens": rng.randint(0, 40), "calls": rng.randint(0, 2)}
                results = []
                for guard in (fast, slow):
                    try:
                        results.append(guard.charge(tenant, usage))
                    except BudgetExceededError as exc:
                        results.append(exc.limit)
                assert isinstance(results[0], int) == isinstance(results[1], int), f"guards disagree on {usage}"
                if isinstance(results[0], int):
                    live.append((results[0], results[1]))
            for tenant in ("a", "b"):
                for limit in CAPS:
                    assert fast.used(tenant, limit) == slow.used(tenant, limit)


def test_concurrent_charges_never_exceed_the_cap():
    guard = BudgetGuard({"tokens": 200})
    successes = []

    def worker():
        ok = 0
        for _ in range(50):
            try:
                guard.charge("acme", {"tokens": 1})
                ok += 1
            except BudgetExceededError:
                pass
        successes.append(ok)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    assert sum(successes) == 200, f"expected exactly 200 successful charges, got {sum(successes)}"
    assert guard.used("acme", "tokens") == 200
