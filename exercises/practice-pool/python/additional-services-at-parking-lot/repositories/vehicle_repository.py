from .in_memory_crud_repository import InMemoryCRUDRepository
from models import Vehicle


class VehicleRepository(InMemoryCRUDRepository[Vehicle]):
    pass

