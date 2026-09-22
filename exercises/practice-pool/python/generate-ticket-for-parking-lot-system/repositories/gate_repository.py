from .in_memory_crud_repository import InMemoryCRUDRepository
from models import Gate


class GateRepository(InMemoryCRUDRepository[Gate]):
    pass


