from datetime import timedelta

from ecom.adapters.map_adapter import MapAdapter
from ecom.libraries.google_maps_api import GoogleMapsApi
from ecom.libraries.google_models import GoogleLocation


class GoogleMapAdapter(MapAdapter):
    def __init__(self) -> None:
        self.google_maps_api = GoogleMapsApi()

    def get_estimated_time(
        self, source_lat: float, source_long: float, destination_lat: float, destination_long: float
    ) -> timedelta:
        return self.google_maps_api.estimate(
            GoogleLocation(source_lat, source_long), GoogleLocation(destination_lat, destination_long))
