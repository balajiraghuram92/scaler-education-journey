import pytest
from fastapi.testclient import TestClient

from tenant_gate import Generation, create_app


class Harness:
    def __init__(self, **kw):
        self.now = [0.0]
        self.calls = 0
        self.fail = False

        async def generate(prompt: str) -> Generation:
            self.calls += 1
            if self.fail:
                raise RuntimeError("provider down")
            return Generation(f"answer to {prompt}", 0.004)

        self.app = create_app(clock=lambda: self.now[0], generate=generate, **kw)
        self.client = TestClient(self.app)

    def chat(self, prompt="hi", tenant="acme", **extra):
        headers = {"X-Tenant-Id": tenant} if tenant else {}
        return self.client.post("/chat", json={"prompt": prompt, **extra}, headers=headers)


@pytest.fixture
def h():
    return Harness(rate=1.0, burst=2, daily_budget_usd=0.01, cache_ttl_s=60)


def test_burst_then_429_with_retry_after(h):
    codes = [h.chat(f"p{i}").status_code for i in range(3)]
    assert codes == [200, 200, 429]
    r = h.chat("p9")
    assert r.status_code == 429 and r.json() == {"error": "rate_limited"}
    assert r.headers["retry-after"] == "1"
    slow = Harness(rate=0.4, burst=1, daily_budget_usd=1.0)
    slow.chat("a")
    assert slow.chat("b").headers["retry-after"] == "3", "Retry-After is the ceil of the 2.5 s wait"


def test_bucket_refills_with_the_injected_clock():
    h = Harness(rate=1.0, burst=2, daily_budget_usd=1.0)
    h.chat("a"), h.chat("b")
    assert h.chat("c").status_code == 429
    h.now[0] += 1.0
    assert h.chat("c").status_code == 200


def test_limits_are_per_tenant(h):
    h.chat("a"), h.chat("b")
    assert h.chat("c").status_code == 429
    assert h.chat("c", tenant="other").status_code == 200


def test_cache_hit_is_free_and_skips_the_provider():
    h = Harness(rate=100, burst=100, daily_budget_usd=0.01)
    first = h.chat("same").json()
    second = h.chat("same").json()
    assert first["cached"] is False and second["cached"] is True
    assert second["cost_usd"] == 0.0 and h.calls == 1
    assert first["answer"] == second["answer"] and first["cost_usd"] == 0.004

    limited = Harness(rate=1.0, burst=2, daily_budget_usd=1.0)
    assert [limited.chat("same").status_code for _ in range(3)] == [200, 200, 429], (
        "the rate limit is checked before the cache, so even cache hits consume a token"
    )


def test_cache_is_isolated_by_tenant_and_ignores_hot_temperatures():
    h = Harness(rate=100, burst=100, daily_budget_usd=1.0)
    h.chat("same")
    assert h.chat("same", tenant="other").json()["cached"] is False
    h.chat("warm", temperature=0.7)
    assert h.chat("warm", temperature=0.7).json()["cached"] is False
    assert h.calls == 4


def test_cache_entries_expire():
    h = Harness(rate=100, burst=100, daily_budget_usd=1.0, cache_ttl_s=60)
    h.chat("same")
    h.now[0] = 59.0
    assert h.chat("same").json()["cached"] is True
    h.now[0] = 61.0
    assert h.chat("same").json()["cached"] is False


def test_budget_exhaustion_is_a_distinct_error_and_resets_next_day():
    h = Harness(rate=100, burst=100, daily_budget_usd=0.01)
    assert h.chat("a").status_code == 200
    assert h.chat("b").status_code == 200
    r = h.chat("c")
    assert r.status_code == 429 and r.json() == {"error": "budget_exhausted"}
    assert "retry-after" not in r.headers and h.calls == 2
    h.now[0] = 86400.0
    assert h.chat("c").status_code == 200


def test_budget_is_per_tenant():
    h = Harness(rate=100, burst=100, daily_budget_usd=0.004)
    assert h.chat("a").status_code == 200
    assert h.chat("b").json() == {"error": "budget_exhausted"}
    assert h.chat("b", tenant="other").status_code == 200


def test_provider_failure_is_502_and_costs_nothing():
    h = Harness(rate=100, burst=100, daily_budget_usd=0.004)
    h.fail = True
    r = h.chat("a")
    assert r.status_code == 502 and r.json() == {"error": "upstream_failed"}
    h.fail = False
    assert h.chat("a").status_code == 200


def test_validation_and_missing_tenant_header(h):
    assert h.chat("hi", tenant=None).status_code == 422
    assert h.client.post("/chat", json={"prompt": ""}, headers={"X-Tenant-Id": "a"}).status_code == 422
    assert h.chat("hi", temperature=2.5).status_code == 422, "temperature must be within 0..2"
