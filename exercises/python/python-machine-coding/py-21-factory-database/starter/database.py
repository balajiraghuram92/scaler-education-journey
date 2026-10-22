from abc import ABC, abstractmethod
from database_type import DatabaseType

class Database(ABC):

    def __init__(self, database_name: str):
        """Store database_name."""
        raise NotImplementedError('TODO: implement __init__')

    def get_database_name(self) -> str:
        """Return the stored name."""
        raise NotImplementedError('TODO: implement get_database_name')

    @abstractmethod
    def database_connection(self) -> None:
        pass

    @abstractmethod
    def supports_type(self) -> DatabaseType:
        pass
