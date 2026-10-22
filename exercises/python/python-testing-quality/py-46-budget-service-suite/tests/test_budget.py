import dataclasses

import pytest

from budget import BudgetExceeded, BudgetService, InMemoryUsageRepo, UsageRepo


@pytest.mark.parametrize(
    ("already_used", "ask", "allowed"),
    [
        pytest.param(0, 1_000, True, id="exactly-at-limit"),
        pytest.param(999, 1, True, id="last-token"),
        pytest.param(1_000, 1, False, id="one-over"),
        pytest.param(0, 1_001, False, id="single-request-over"),
    ],
)
def test_limit_boundary(service, repo, already_used, ask, allowed):
    if already_used:
        repo.add("acme", already_used)
    if allowed:
        assert service.charge("acme", ask) == already_used + ask, "charge returns the new running total"
    else:
        with pytest.raises(BudgetExceeded):
            service.charge("acme", ask)


@pytest.mark.parametrize("bad", [0, -5], ids=["zero", "negative"])
def test_rejects_non_positive(service, bad):
    with pytest.raises(ValueError, match="tokens must be positive"):
        service.charge("acme", bad)


def test_rejected_charge_has_no_side_effect(service, repo):
    service.charge("acme", 900)
    with pytest.raises(BudgetExceeded) as excinfo:
        service.charge("acme", 200)
    exc = excinfo.value
    assert (exc.tenant, exc.used, exc.requested, exc.limit) == ("acme", 900, 200, 1_000)
    assert service.remaining("acme") == 100, "a rejected charge must not change stored usage"
    assert repo.get("acme") == 900


def test_exception_message_format(service):
    service.charge("acme", 900)
    with pytest.raises(BudgetExceeded, match=r"acme: 900\+200 exceeds limit 1000"):
        service.charge("acme", 200)
    assert issubclass(BudgetExceeded, Exception)


def test_tenants_are_isolated(service):
    service.charge("acme", 800)
    assert service.charge("globex", 800) == 800
    assert service.remaining("acme") == 200


def test_repo_unknown_tenant_and_running_total():
    repo = InMemoryUsageRepo()
    assert repo.get("nobody") == 0, "unknown tenants have usage 0"
    assert repo.add("acme", 10) == 10
    assert repo.add("acme", 5) == 15
    assert repo.get("acme") == 15
    assert dataclasses.is_dataclass(repo)


def test_remaining_reflects_seeded_usage(service, repo):
    assert service.remaining("acme") == 1_000
    repo.add("acme", 250)
    assert service.remaining("acme") == 750, "service must read usage through the repo"


def test_service_depends_only_on_the_protocol():
    class CountingRepo:
        def __init__(self) -> None:
            self.data: dict[str, int] = {}

        def get(self, tenant: str) -> int:
            return self.data.get(tenant, 0)

        def add(self, tenant: str, tokens: int) -> int:
            self.data[tenant] = self.get(tenant) + tokens
            return self.data[tenant]

    custom: UsageRepo = CountingRepo()
    svc = BudgetService(custom, limit=10)
    assert svc.charge("t", 10) == 10
    with pytest.raises(BudgetExceeded):
        svc.charge("t", 1)
