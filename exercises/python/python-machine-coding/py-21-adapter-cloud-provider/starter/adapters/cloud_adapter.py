from abc import ABC, abstractmethod
from models.connection import Connection

class CloudAdapter(ABC):
    @abstractmethod
    def create_connection(self, user_id: int) -> Connection:
        pass
