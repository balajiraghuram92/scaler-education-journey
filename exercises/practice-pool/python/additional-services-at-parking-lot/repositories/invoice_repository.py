from .in_memory_crud_repository import InMemoryCRUDRepository
from models import Invoice


class InvoiceRepository(InMemoryCRUDRepository[Invoice]):
    pass

