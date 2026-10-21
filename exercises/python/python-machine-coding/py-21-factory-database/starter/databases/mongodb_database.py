from database import Database
from database_type import DatabaseType

class MongoDBDatabase(Database):
    def __init__(self, database_name: str):
        super().__init__(database_name)

    def database_connection(self) -> None:
        # Implement the logic to connect MongoDB Database
        print("Connecting to MongoDB Database")

    def supports_type(self) -> DatabaseType:
        return DatabaseType.MONGO_DB
