from database import Database
from database_type import DatabaseType

class DatabaseFactory:

    @staticmethod
    def create_database(db_type: DatabaseType, name: str) -> Database:
        """Return MySQLDatabase, PostgreSQLDatabase or MongoDBDatabase (from databases/) for the given DatabaseType, constructed with name. Raise ValueError for anything else."""
        raise NotImplementedError('TODO: implement create_database')
