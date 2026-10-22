from datetime import timedelta

from ecom.libraries.google_models import GoogleLocation


class GoogleMapsApi:
    """Stand-in for the third-party SDK: takes its own GoogleLocation type and returns a timedelta."""

    def estimate(self, source: GoogleLocation, destination: GoogleLocation) -> timedelta:
        degrees = abs(source.latitude - destination.latitude) + abs(source.longitude - destination.longitude)
        return timedelta(minutes=round(degrees * 100))
