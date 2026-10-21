from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

TripStatus = Literal["requested", "active", "done"]
CAPPED_ZONES = {"stadium"}


class TripCreate(BaseModel):
    rider_id: int = Field(gt=0)
    pickup: str = Field(min_length=3, max_length=200)
    dropoff: str = Field(min_length=3, max_length=200)
    distance_km: float = Field(gt=0, le=200)
    zone: str = "default"


class TripOut(BaseModel):
    id: UUID
    rider_id: int
    pickup: str
    dropoff: str
    status: TripStatus


class TripRecord(TripOut):  # internal: never exposed
    fare_cents: int
    driver_payout_cents: int


class SurgeCapExceeded(Exception):
    def __init__(self, zone: str) -> None:
        super().__init__(zone)
        self.zone = zone


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
    return record


@router.get("")
async def list_trips(
    trip_status: Annotated[TripStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[TripOut]:
    trips = [t for t in _TRIPS.values() if trip_status is None or t.status == trip_status]
    return trips[:limit]


@router.get("/{trip_id}")
async def get_trip(trip_id: UUID) -> TripOut:
    trip = _TRIPS.get(trip_id)
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="trip not found")
    return trip


@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel a trip",
    responses={404: {"description": "Trip not found"}},
)
async def cancel_trip(trip_id: UUID) -> None:
    if _TRIPS.pop(trip_id, None) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="trip not found")


app = FastAPI(title="Trip Service", version="1.0.0")
app.include_router(router)


@app.exception_handler(SurgeCapExceeded)
async def surge_cap_handler(request: Request, exc: SurgeCapExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"error": "surge_cap_exceeded", "zone": exc.zone},
    )
