import inspect
from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from main import _TRIPS, app

client = TestClient(app)

GOOD = {"rider_id": 7, "pickup": "Airport", "dropoff": "Hotel", "distance_km": 12.5}


@pytest.fixture(autouse=True)
def clean_storage() -> Iterator[None]:
    _TRIPS.clear()
    yield
    _TRIPS.clear()


def test_create_returns_201_and_filters_internal_fields():
    r = client.post("/trips", json=GOOD)
    assert r.status_code == 201, f"expected 201, got {r.status_code}: {r.text}"
    body = r.json()
    assert sorted(body) == ["dropoff", "id", "pickup", "rider_id", "status"], "fare and payout must not be exposed"
    assert body["status"] == "requested"
    assert body["pickup"] == "Airport" and body["rider_id"] == 7


def test_fare_and_payout_are_computed_and_stored_internally():
    client.post("/trips", json={**GOOD, "distance_km": 10})
    (record,) = _TRIPS.values()
    assert record.fare_cents == 250 + round(10 * 120), "fare is 250 + round(distance_km * 120) cents"
    assert record.driver_payout_cents == round(record.fare_cents * 0.8), "payout is round(fare * 0.8)"


def test_validation_rules_and_boundaries():
    assert client.post("/trips", json={**GOOD, "pickup": "x"}).status_code == 422, "pickup must be >= 3 chars"
    assert client.post("/trips", json={**GOOD, "distance_km": 0}).status_code == 422, "distance must be > 0"
    assert client.post("/trips", json={**GOOD, "distance_km": 200.5}).status_code == 422, "distance must be <= 200"
    assert client.post("/trips", json={**GOOD, "rider_id": 0}).status_code == 422, "rider_id must be > 0"
    assert client.post("/trips", json={**GOOD, "dropoff": "d" * 201}).status_code == 422, "dropoff max 200 chars"
    ok = client.post("/trips", json={**GOOD, "distance_km": 200, "pickup": "abc", "zone": "downtown"})
    assert ok.status_code == 201, "distance 200, a 3-char pickup and a normal zone are valid"
    assert client.post("/trips", json=GOOD).status_code == 201, "zone is optional"


def test_capped_zone_maps_to_409():
    r = client.post("/trips", json={**GOOD, "zone": "stadium"})
    assert r.status_code == 409
    assert r.json() == {"error": "surge_cap_exceeded", "zone": "stadium"}
    assert not _TRIPS, "a rejected trip must not be stored"


def test_get_returns_trip_without_internal_fields():
    created = client.post("/trips", json=GOOD).json()
    r = client.get(f"/trips/{created['id']}")
    assert r.status_code == 200
    assert r.json() == created, "GET must return the same public fields as POST"


def test_get_unknown_and_malformed_ids():
    r = client.get(f"/trips/{uuid4()}")
    assert r.status_code == 404
    assert r.json() == {"detail": "trip not found"}
    assert client.get("/trips/not-a-uuid").status_code == 422, "a malformed UUID is a validation error"


def test_list_limit_and_status_filter():
    for _ in range(3):
        client.post("/trips", json=GOOD)
    assert len(client.get("/trips").json()) == 3
    assert len(client.get("/trips", params={"limit": 2}).json()) == 2
    assert len(client.get("/trips", params={"status": "requested"}).json()) == 3
    assert client.get("/trips", params={"status": "done"}).json() == []
    for item in client.get("/trips").json():
        assert "fare_cents" not in item and "driver_payout_cents" not in item


def test_list_rejects_invalid_query_values():
    assert client.get("/trips", params={"limit": 0}).status_code == 422
    assert client.get("/trips", params={"limit": 101}).status_code == 422
    assert client.get("/trips", params={"status": "bogus"}).status_code == 422


def test_delete_then_get():
    trip_id = client.post("/trips", json=GOOD).json()["id"]
    r = client.delete(f"/trips/{trip_id}")
    assert r.status_code == 204
    assert r.content == b"", "204 must have no body"
    assert client.get(f"/trips/{trip_id}").status_code == 404
    assert client.delete(f"/trips/{trip_id}").status_code == 404, "deleting twice is a 404"


def test_openapi_documents_trips_and_handlers_are_async():
    schema = client.get("/openapi.json").json()
    assert schema["info"]["title"] == "Trip Service" and schema["info"]["version"] == "1.0.0"
    assert "/trips" in schema["paths"]
    assert "/trips/{trip_id}" in schema["paths"]
    assert "404" in schema["paths"]["/trips/{trip_id}"]["delete"]["responses"], "document the DELETE 404"
    endpoints = [r.endpoint for r in app.routes if getattr(r, "path", "").startswith("/trips")]
    assert endpoints and all(inspect.iscoroutinefunction(e) for e in endpoints), "route handlers must be async def"
