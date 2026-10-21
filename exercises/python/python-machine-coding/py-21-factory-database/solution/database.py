from abc import ABC, abstractmethod
from database_type import DatabaseType

class Database(ABC):
    def __init__(self, database_name: str):
        self.database_name = database_name

    def get_database_name(self) -> str:
        return self.database_name

    @abstractmethod
    def database_connection(self) -> None:
        pass
    
    @abstractmethod
    def supports_type(self) -> DatabaseType:
        pass
