import inspect
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from main import _RECORDS, app

client = TestClient(app)

BODY = {"customer_id": 1, "amount_cents": 1999, "currency": "USD"}
KEY = {"Idempotency-Key": "order-1234-attempt"}


@pytest.fixture(autouse=True)
def clean() -> Iterator[None]:
    _RECORDS.clear()
    yield
    _RECORDS.clear()


def test_first_call_creates_a_captured_payment():
    r = client.post("/payments", json=BODY, headers=KEY)
    assert r.status_code == 201, f"expected 201, got {r.status_code}: {r.text}"
    data = r.json()
    UUID(data["id"])
    assert data["status"] == "captured"
    assert (data["customer_id"], data["amount_cents"], data["currency"]) == (1, 1999, "USD")
    assert "Idempotent-Replayed" not in r.headers, "the first response is not a replay"


def test_replay_returns_stored_payment():
    first = client.post("/payments", json=BODY, headers=KEY)
    again = client.post("/payments", json=BODY, headers=KEY)
    assert (first.status_code, again.status_code) == (201, 200), "replay must answer 200"
    assert first.json() == again.json(), "a replay returns the stored payment with the same id"
    assert again.headers["Idempotent-Replayed"] == "true"
    assert len(_RECORDS) == 1, "no second payment may be created"


def test_different_keys_create_different_payments():
    a = client.post("/payments", json=BODY, headers={"Idempotency-Key": "key-aaaaaaaa"})
    b = client.post("/payments", json=BODY, headers={"Idempotency-Key": "key-bbbbbbbb"})
    assert (a.status_code, b.status_code) == (201, 201)
    assert a.json()["id"] != b.json()["id"]
    assert len(_RECORDS) == 2


def test_key_reuse_with_different_body_is_409_envelope():
    client.post("/payments", json=BODY, headers=KEY)
    r = client.post("/payments", json={**BODY, "amount_cents": 5}, headers=KEY)
    assert r.status_code == 409
    err = r.json()["error"]
    assert err["code"] == "idempotency_key_reuse"
    assert isinstance(err["message"], str) and err["message"]
    assert err["fields"] == [], "an ApiError envelope has an empty fields list"
    assert len(_RECORDS) == 1, "the conflicting request must not replace the stored payment"


def test_missing_key_uses_the_envelope():
    missing = client.post("/payments", json=BODY)
    assert missing.status_code == 422
    err = missing.json()["error"]
    assert err["code"] == "validation_error"
    assert any("idempotency" in f["loc"].lower() for f in err["fields"]), "a field location must mention the header"
    assert not _RECORDS


def test_short_key_is_rejected():
    r = client.post("/payments", json=BODY, headers={"Idempotency-Key": "abc"})
    assert r.status_code == 422, "keys shorter than 8 characters are invalid"
    assert r.json()["error"]["code"] == "validation_error"
    assert client.post("/payments", json=BODY, headers={"Idempotency-Key": "12345678"}).status_code == 201


def test_invalid_body_fields_are_reported_by_dotted_location():
    r = client.post("/payments", json={**BODY, "amount_cents": 0}, headers=KEY)
    assert r.status_code == 422
    fields = r.json()["error"]["fields"]
    assert any("amount_cents" in f["loc"] and isinstance(f["msg"], str) for f in fields), "loc is a dotted string"
    assert client.post("/payments", json={**BODY, "amount_cents": 1_000_001}, headers=KEY).status_code == 422
    assert client.post("/payments", json={**BODY, "currency": "GBP"}, headers=KEY).status_code == 422
    assert client.post("/payments", json={**BODY, "customer_id": 0}, headers=KEY).status_code == 422
    assert client.post("/payments", json={**BODY, "amount_cents": 1_000_000}, headers=KEY).status_code == 201


def test_concurrent_retries_create_exactly_one_payment():
    def call(_: int) -> int:
        return TestClient(app).post("/payments", json=BODY, headers=KEY).status_code  # one client per thread

    with ThreadPoolExecutor(max_workers=10) as pool:
        codes = list(pool.map(call, range(20)))
    assert codes.count(201) == 1, f"exactly one request may create the payment, got {codes.count(201)}"
    assert codes.count(200) == 19
    assert len(_RECORDS) == 1


def test_endpoint_is_a_plain_def_and_router_is_mounted():
    routes = [r for r in app.routes if getattr(r, "path", "") == "/payments"]
    assert routes, "POST /payments must be mounted"
    assert not inspect.iscoroutinefunction(routes[0].endpoint), "use a plain `def` so it runs in the threadpool"
