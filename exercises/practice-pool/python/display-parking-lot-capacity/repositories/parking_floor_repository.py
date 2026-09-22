from .in_memory_crud_repository import InMemoryCRUDRepository
from models import ParkingFloor


class ParkingFloorRepository(InMemoryCRUDRepository[ParkingFloor]):
    pass

