from .in_memory_crud_repository import InMemoryCRUDRepository
from models import Ticket


class TicketRepository(InMemoryCRUDRepository[Ticket]):
    pass

