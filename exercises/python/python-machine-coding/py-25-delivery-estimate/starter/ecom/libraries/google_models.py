from dataclasses import dataclass


@dataclass(frozen=True)
class GoogleLocation:
    latitude: float
    longitude: float
