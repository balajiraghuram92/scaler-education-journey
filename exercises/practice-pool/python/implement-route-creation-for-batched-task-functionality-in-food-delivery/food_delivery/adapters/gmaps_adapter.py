from .maps_adapter import MapsAdapter
from typing import List
from food_delivery.models import Location
from food_delivery.libs.gmap import GLocation, get_optimized_route


class GMapsMapsAdapter(MapsAdapter):

    def build_route(self, locations: List[Location]) -> List[Location]:
        g_locations = [
            GLocation(location.latitude, location.longitude)
            for location in locations
        ]

        optimized_route: List[GLocation] = get_optimized_route(g_locations)
        return [
            Location(latitude=location.lat, longitude=location.lng)
            for location in optimized_route
        ]
