from .map_adapter import MapAdapter
from ecom.libraries import GoogleMapsApi
from ecom.libraries.models import GoogleLocation
from datetime import timedelta


class GoogleMapAdapter(MapAdapter):
    google_maps_api: GoogleMapsApi

    def __init__(self):
        self.google_maps_api = GoogleMapsApi()

    def get_estimated_time(
            self,
            source_lat: float,
            source_long: float,
            destination_lat: float,
            destination_long: float
    ) -> timedelta:
        return self.google_maps_api.estimate(
            GoogleLocation(source_lat, source_long),
            GoogleLocation(destination_lat, destination_long)
        )
