import pytest
from fastapi.testclient import TestClient

import main
from conftest import bearer, make_settings, make_token
from routers.echo import get_echo_agent


class _FakeResult:
    output = {"message": "hi"}


class _FakeAgent:
    """Stands in for the Muse agent so no test makes a network call."""

    def __init__(self, fail=False):
        self.calls = 0
        self.fail = fail

    async def run(self, prompt):
        self.calls += 1
        if self.fail:
            raise RuntimeError("upstream exploded")
        return _FakeResult()


def test_health_is_public_liveness(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_reports_503_when_database_unavailable(client):
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["database"] == "down"


@pytest.mark.parametrize("path", ["/me", "/echo", "/agent_test"])
def test_protected_routes_require_a_token(client, app, path):
    fake = _FakeAgent()
    app.dependency_overrides[get_echo_agent] = lambda: fake
    response = client.get(path)
    assert response.status_code == 401
    assert fake.calls == 0  # no paid model call without auth


def test_echo_with_token_calls_agent(client, app):
    fake = _FakeAgent()
    app.dependency_overrides[get_echo_agent] = lambda: fake
    response = client.get("/echo", headers=bearer(make_token()))
    assert response.status_code == 200
    assert response.json() == {"message": "hi"}
    assert fake.calls == 1


def test_echo_upstream_failure_is_502_without_details(client, app):
    app.dependency_overrides[get_echo_agent] = lambda: _FakeAgent(fail=True)
    response = client.get("/echo", headers=bearer(make_token()))
    assert response.status_code == 502
    assert "exploded" not in response.text


def test_agent_graph_with_token(client):
    response = client.get("/agent_test", headers=bearer(make_token()))
    assert response.status_code == 200
    assert response.json()["output_txt"] == "graph says: Hello"


def test_per_user_rate_limit_returns_429():
    app = main.build_app(make_settings(rate_limit_per_minute=2))
    fake = _FakeAgent()
    app.dependency_overrides[get_echo_agent] = lambda: fake
    client = TestClient(app)
    alice, bob = bearer(make_token(nameid="1")), bearer(make_token(nameid="2"))
    assert [client.get("/echo", headers=alice).status_code for _ in range(3)] == [200, 200, 429]
    assert client.get("/echo", headers=bob).status_code == 200  # limit is per user
    assert fake.calls == 3


@pytest.mark.parametrize("path", ["/docs", "/redoc", "/openapi.json"])
def test_docs_disabled_by_default(client, path):
    assert client.get(path).status_code == 404


def test_docs_enabled_by_flag():
    client = TestClient(main.build_app(make_settings(enable_docs=True)))
    assert client.get("/openapi.json").status_code == 200
    assert client.get("/docs").status_code == 200
