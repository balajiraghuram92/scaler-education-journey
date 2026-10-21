from functools import singledispatch

from trip import Trip


@singledispatch
def estimate_fare(x):
    raise NotImplementedError


@estimate_fare.register
def _(distance: float):
    return 15 * distance


@estimate_fare.register
def _(route_code: str):
    fares = {
        "HSR-AIRPORT": 600,
        "MG-AIRPORT": 550,
    }
    return fares.get(route_code, 0)


@estimate_fare.register
def _(trip: Trip):
    return 15 * trip.distance_km
