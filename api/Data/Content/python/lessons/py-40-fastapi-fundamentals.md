# FastAPI Fundamentals

FastAPI is the default way Python teams ship AI and backend APIs, so interviewers assume you can build an endpoint and then ask what happens at the edges: which fields leak into the response, why a validation error is a 422, where a `def` handler actually runs, and why one blocking call inside an `async def` handler stalls the whole server. This lesson covers the request and response pipeline precisely enough that you can predict behaviour instead of guessing. The code targets FastAPI 0.11x with Pydantic v2.

## Concepts Covered

### Path parameters, query parameters and bodies

FastAPI reads the function signature. A name that appears in the path template is a **path parameter**; a scalar parameter that does not is a **query parameter**; a Pydantic model parameter is the **request body**. Type annotations drive parsing and validation, and a failure becomes a 422 response before your function runs.

```python
from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

TripStatus = Literal["requested", "active", "done"]


class TripCreate(BaseModel):
    rider_id: int = Field(gt=0)
    pickup: str = Field(min_length=3, max_length=200)
    dropoff: str = Field(min_length=3, max_length=200)
    distance_km: float = Field(gt=0, le=200)
    zone: str = "default"
```

Three rules matter in practice. Constraints on query parameters go through `Annotated[..., Query(...)]` (for example `ge=1, le=100`, or `pattern=` for a regular expression). A list-valued query parameter needs an explicit `Query()`, otherwise FastAPI would treat a list as a body. And with two or more body parameters FastAPI expects a JSON object keyed by parameter name, while a single body parameter is the object itself (`Body(embed=True)` forces keying).

> **Pitfall:** Route order matters. If `/users/{user_id}` is declared before `/users/me`, the request for `/users/me` matches the first route and `me` fails to parse as an `int`, giving a 422. Declare fixed paths first.

### response_model, filtering and status codes

Never return your storage model directly. Declare what clients may see, and FastAPI validates and filters the returned value against it, so internal fields cannot leak. Since FastAPI 0.89 the return annotation does this job; `response_model=` on the decorator takes precedence when both are given.

```python
class TripOut(BaseModel):
    id: UUID
    rider_id: int
    pickup: str
    dropoff: str
    status: TripStatus


class TripRecord(TripOut):                 # internal: never exposed
    fare_cents: int
    driver_payout_cents: int


CAPPED_ZONES = {"stadium"}
_TRIPS: dict[UUID, TripRecord] = {}

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_trip(body: TripCreate) -> TripOut:
    if body.zone in CAPPED_ZONES:
        raise SurgeCapExceeded(body.zone)
    fare = 250 + round(body.distance_km * 120)
    record = TripRecord(
        id=uuid4(),
        rider_id=body.rider_id,
        pickup=body.pickup,
        dropoff=body.dropoff,
        status="requested",
        fare_cents=fare,
        driver_payout_cents=round(fare * 0.8),
    )
    _TRIPS[record.id] = record
    return record                           # serialised as TripOut: fare fields are dropped
```

Returning a `TripRecord` where `TripOut` is declared type-checks because it is a subclass, and the response contains only `TripOut` fields. Related switches are `response_model_exclude_none=True` (omit null fields) and `response_model_exclude_unset=True` (omit fields you never set). The default status for a POST is 200, so say `201` explicitly for creation and `204` for deletion with no body. Returning a `Response` object directly bypasses `response_model` entirely, including the filtering, which is occasionally a security bug.

### HTTPException and custom exception handlers

Raise `HTTPException(status_code=..., detail=...)` for expected client errors; `detail` becomes the JSON body `{"detail": ...}`. For domain errors, define your own exception and register a handler so that the translation to HTTP lives in one place and services stay free of HTTP concepts.

```python
class SurgeCapExceeded(Exception):
    def __init__(self, zone: str) -> None:
        super().__init__(zone)
        self.zone = zone


@router.get("/{trip_id}")
async def get_trip(trip_id: UUID) -> TripOut:
    trip = _TRIPS.get(trip_id)
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="trip not found")
    return trip


@router.get("")
async def list_trips(
    trip_status: Annotated[TripStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[TripOut]:
    trips = [t for t in _TRIPS.values() if trip_status is None or t.status == trip_status]
    return trips[:limit]


app = FastAPI(title="Trip Service", version="1.0.0")
app.include_router(router)


@app.exception_handler(SurgeCapExceeded)
async def surge_cap_handler(request: Request, exc: SurgeCapExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"error": "surge_cap_exceeded", "zone": exc.zone},
    )
```

Note the `alias="status"` on the query parameter: the Python name `trip_status` avoids shadowing the imported `status` module while the public API stays `?status=active`. Validation failures raise `RequestValidationError`, which has a default handler producing a 422 with a `detail` list of `loc`, `msg` and `type`; you can register your own handler for `RequestValidationError` to wrap errors in your API's envelope.

### Sync versus async path operations

This is the most commonly misunderstood FastAPI behaviour. An `async def` path operation runs **on the event loop**: if it blocks, nothing else is served. A plain `def` path operation is run **in a threadpool** (via AnyIO, with a default limit of 40 concurrent threads), so it can block without freezing the loop, but it is bounded by the pool and subject to thread-safety concerns.

```python
import asyncio
import time


@router.get("/{trip_id}/receipt")
def receipt(trip_id: UUID) -> dict[str, str]:
    time.sleep(0.5)                  # blocking sync library: fine here, it runs in the threadpool
    return {"trip": str(trip_id)}


@router.get("/{trip_id}/eta")
async def eta(trip_id: UUID) -> dict[str, int]:
    await asyncio.sleep(0.5)         # awaiting: the loop serves other requests meanwhile
    return {"minutes": 7}


@router.get("/{trip_id}/broken")
async def broken(trip_id: UUID) -> dict[str, str]:
    time.sleep(0.5)                  # BUG: blocks the loop; every request waits
    return {"trip": str(trip_id)}
```

The rule: use `async def` only if everything you call inside is awaited or non-blocking; use `def` when calling blocking libraries (a sync ORM session, a sync SDK). Dependencies follow the same rule. When the threadpool is saturated, `def` endpoints queue, which looks like latency with low CPU. Because `def` endpoints run on multiple threads, module-level mutable state (like the `_TRIPS` dict above) needs a lock once you stop using the single-threaded `async def` form.

### APIRouter and OpenAPI

`APIRouter(prefix="/trips", tags=["trips"])` groups related endpoints per module and keeps `main.py` small; `app.include_router(router)` mounts it. FastAPI builds an OpenAPI 3 document from your signatures, models, `summary`, `description`, `responses` and `tags`, served at `/openapi.json`, with Swagger UI at `/docs` and ReDoc at `/redoc`. Document the non-obvious responses:

```python
@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel a trip",
    responses={404: {"description": "Trip not found"}},
)
async def cancel_trip(trip_id: UUID) -> None:
    if _TRIPS.pop(trip_id, None) is None:
        raise HTTPException(status_code=404, detail="trip not found")
```

In production you often disable the docs UI (`FastAPI(docs_url=None, redoc_url=None)`); the schema endpoint stays on unless you also set `openapi_url=None`. The schema is a contract worth testing and a source for generated clients.

### TestClient

`fastapi.testclient.TestClient` wraps the app in a synchronous httpx-based client (the `httpx` package must be installed), so you test the whole stack, including validation and serialisation, without a running server.

```python
from fastapi.testclient import TestClient

client = TestClient(app)


def test_create_and_fetch_trip() -> None:
    payload = {"rider_id": 7, "pickup": "Airport", "dropoff": "Hotel", "distance_km": 12.5}
    created = client.post("/trips", json=payload)
    assert created.status_code == 201
    body = created.json()
    assert "fare_cents" not in body                # filtered by the response model
    assert client.get(f"/trips/{body['id']}").status_code == 200


def test_validation_error_is_422() -> None:
    bad = {"rider_id": 7, "pickup": "x", "dropoff": "Hotel", "distance_km": 5}
    assert client.post("/trips", json=bad).status_code == 422
```

Lifespan start-up and shutdown handlers run only when you use the client as a context manager (`with TestClient(app) as client:`). Forgetting that is a standard cause of "works in production, `AttributeError` in tests".

## Practical Backend Scenario

You are building the trip-booking API for a ride-hailing product, consumed by a mobile app and by a partner integration. The mobile team must never see fare and payout fields, the stadium zone has a surge cap that must produce a 409 the app understands, and the on-call engineer wants to know why p99 doubled after a teammate added a PDF receipt endpoint that uses a sync library. The pieces above resolve each issue: a separate output model enforces the contract, a custom exception handler maps the business rule to a stable error body, and moving the sync PDF call into a plain `def` endpoint (or `asyncio.to_thread`) takes it off the loop. The tests assert on filtering, on 409 and 422 bodies, and on the OpenAPI document so that the contract cannot change unnoticed.

## Practice Loop

1. Build the trip service above in a fresh virtual environment with `fastapi`, `uvicorn` and `httpx` installed, and run it with `uvicorn main:app --reload`.
2. Open `/docs`, call each endpoint, and compare the schemas of `TripCreate` and `TripOut` in the OpenAPI document.
3. Add a field `internal_notes` to `TripRecord` and confirm it never appears in a response.
4. Add `/trips/active` after `/trips/{trip_id}`, observe the 422 for the fixed path, then fix the order.
5. Add the `receipt` and `broken` endpoints, and use `curl` in parallel (for example `xargs -P`) to see how the blocking `async def` version serialises requests.
6. Write pytest tests for 201, 404, 409, 422 and the `exclude_none` behaviour, then complete the coding assignments below.

## Evidence of Understanding

- I can say where a parameter comes from (path, query, body, header) from the function signature alone.
- I can explain why returning a subclass instance leaks nothing when a parent `response_model` is declared, and when a returned `Response` object bypasses it.
- I can map a domain exception to an HTTP response with a registered handler, and distinguish `HTTPException` from `RequestValidationError`.
- I can state where `def` and `async def` endpoints run and what the threadpool limit means for latency.
- I can explain why the route order matters and why default POST status is 200.
- I can write `TestClient` tests, and know when the lifespan runs.

## Interview Questions to Rehearse

### Q: Where does a `def` endpoint run compared with an `async def` endpoint?
`async def` runs on the event loop thread, so it must never block. A plain `def` endpoint is dispatched to a threadpool (AnyIO, default 40 threads), so blocking calls are safe but throughput is bounded by the pool and shared state needs locking. Choose by what you call inside: awaitable libraries go in `async def`, blocking libraries in `def`.

### Q: How do you stop internal fields leaking from an endpoint?
Declare a separate output model and use it as the return annotation or `response_model`. FastAPI validates the returned object against it and drops fields it does not declare. Keep input, output and storage models distinct, and avoid returning raw `Response` objects, which skip the filtering.

### Q: Why does a bad request return 422 and how do you customise it?
Request validation failures raise `RequestValidationError`, handled by default into a 422 with a `detail` list containing the location, message and error type of each problem. Register an exception handler for `RequestValidationError` to return your own envelope, and keep the machine-readable `loc` information.

### Q: How would you map a business rule violation to an HTTP response without importing FastAPI in the service layer?
Define a domain exception and register `@app.exception_handler(MyError)` that returns a `JSONResponse` with a stable status code and error code. The service raises plain Python exceptions, the HTTP layer owns translation, and tests assert the contract at the boundary.

### Q: What does `TestClient` give you, and what does it not?
It runs the real ASGI app in-process through a sync httpx-based client, exercising routing, validation, dependencies and serialisation without a network. It does not run lifespan handlers unless used as a context manager, and it does not reveal concurrency problems such as event-loop blocking or multi-worker state differences.

### Q: Two uvicorn workers and an in-memory dict: what breaks?
Each worker is a separate process with its own memory, so a trip created through one worker may be missing on the next request routed to the other. Shared state belongs in a database or cache, not process memory.

## Common Pitfalls

- Using `async def` and then calling a blocking library, which freezes every request.
- Returning an ORM or storage model directly and leaking columns such as password hashes or cost fields.
- Declaring `/items/{id}` before `/items/me`, so the fixed path is captured by the parameterised one.
- Assuming POST returns 201 by default; it returns 200 unless you set `status_code`.
- Using mutable module state in multi-threaded `def` endpoints, or with several workers, and then seeing lost updates or missing data.
- Forgetting the `with` on `TestClient` when the app relies on lifespan start-up.
- Leaving `/docs` and `/openapi.json` exposed on an internal-only API without realising what they reveal.
- Raising `HTTPException` from deep inside domain code, which couples the domain layer to HTTP.

## Suggested Extension

Add cursor-based pagination to `GET /trips` (an opaque `cursor` query parameter and a `next_cursor` in the response model), generate the OpenAPI document in a test, and assert that the schema for `TripOut` has no fare fields. Then fail the test intentionally by adding a field to `TripOut` to see the contract test do its job.
