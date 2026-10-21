from typing import Annotated, Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

TripStatus = Literal["requested", "active", "done"]
CAPPED_ZONES = {"stadium"}


class TripCreate(BaseModel):
    """Request body for POST /trips.

    Add these fields:
    - rider_id: int > 0
    - pickup, dropoff: str, 3 to 200 characters
    - distance_km: float > 0 and <= 200
    - zone: str, default "default"
    """


class TripOut(BaseModel):
    """Public response model: id (UUID), rider_id, pickup, dropoff, status (TripStatus)."""


class TripRecord(TripOut):
    """Internal record: TripOut plus fare_cents and driver_payout_cents (both int). Never exposed."""


class SurgeCapExceeded(Exception):
    """Raised for a capped zone; keep the zone on ``self.zone``."""

    def __init__(self, zone: str) -> None:
        super().__init__(zone)
        self.zone = zone


_TRIPS: dict[UUID, TripRecord] = {}  # in-memory storage; the tests clear it between runs

router = APIRouter(prefix="/trips", tags=["trips"])

# TODO: implement the five routes on ``router`` (all ``async def``):
#   POST   ""            -> 201, returns TripOut. fare = 250 + round(distance_km * 120) cents,
#                           payout = round(fare * 0.8). Neither may appear in the response.
#                           A zone in CAPPED_ZONES raises SurgeCapExceeded.
#   GET    ""            -> list; ?status= (alias for a parameter named trip_status) and
#                           ?limit= (1 to 100, default 20)
#   GET    "/{trip_id}"  -> UUID path parameter; 404 {"detail": "trip not found"}
#   DELETE "/{trip_id}"  -> 204 with no body, or 404; document the 404 in ``responses``

app = FastAPI(title="Trip Service", version="1.0.0")
app.include_router(router)

# TODO: register an exception handler that maps SurgeCapExceeded to
#   409 {"error": "surge_cap_exceeded", "zone": "<zone>"}
