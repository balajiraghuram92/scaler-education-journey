from .in_memory_crud_repository import InMemoryCRUDRepository
from models import ParkingSpot


class ParkingSpotRepository(InMemoryCRUDRepository[ParkingSpot]):
    pass

