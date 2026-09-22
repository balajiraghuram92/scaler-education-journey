from .in_memory_crud_repository import InMemoryCRUDRepository
from models import Slab


class SlabRepository(InMemoryCRUDRepository[Slab]):
    pass
