from .models import GoogleLocation
from datetime import timedelta


class GoogleMapsApi:

    def estimate(
            self,
            source: GoogleLocation,
            destination: GoogleLocation
    ) -> timedelta:
        return timedelta(
            minutes=GoogleMapsApi.euclidean_distance(source, destination)
        )

    @classmethod
    def euclidean_distance(
            cls,
            source: GoogleLocation,
            destination: GoogleLocation
    ) -> float:
        return ((source.latitude - destination.latitude)**2 + (source.longitude - destination.longitude)**2)**0.5

