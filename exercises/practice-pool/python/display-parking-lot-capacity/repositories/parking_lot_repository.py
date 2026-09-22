from .in_memory_crud_repository import InMemoryCRUDRepository
from models import ParkingLot


class ParkingLotRepository(InMemoryCRUDRepository[ParkingLot]):
    pass

