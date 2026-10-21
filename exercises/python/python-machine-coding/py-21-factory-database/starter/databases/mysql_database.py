from database import Database
from database_type import DatabaseType

class MySQLDatabase(Database):
    def __init__(self, database_name: str):
        super().__init__(database_name)

    def database_connection(self) -> None:
        # Implement the logic to connect MYSQL Database
        print("Connecting to MYSQL Database")

    def supports_type(self) -> DatabaseType:
        return DatabaseType.MYSQL
