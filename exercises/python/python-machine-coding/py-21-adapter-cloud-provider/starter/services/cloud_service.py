from abc import ABC, abstractmethod
from models.connection import Connection
from exceptions.exceptions import UserNotFoundException

class CloudService(ABC):
    @abstractmethod
    def create_connection(self, user_id: int) -> Connection:
        pass
