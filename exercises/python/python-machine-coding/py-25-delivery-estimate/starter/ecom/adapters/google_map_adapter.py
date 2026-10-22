from datetime import timedelta
from ecom.adapters.map_adapter import MapAdapter
from ecom.libraries.google_maps_api import GoogleMapsApi
from ecom.libraries.google_models import GoogleLocation

class GoogleMapAdapter(MapAdapter):

    def __init__(self) -> None:
        """Create the GoogleMapsApi SDK object and keep it."""
        raise NotImplementedError('TODO: implement __init__')

    def get_estimated_time(self, source_lat: float, source_long: float, destination_lat: float, destination_long: float) -> timedelta:
        """Wrap the source and destination coordinates in GoogleLocation, call GoogleMapsApi.estimate and return its timedelta."""
        raise NotImplementedError('TODO: implement get_estimated_time')
