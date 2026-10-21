from database import Database
from database_type import DatabaseType

class DatabaseFactory:
    @staticmethod
    def create_database(db_type: DatabaseType, name: str) -> Database:
        if db_type == DatabaseType.MYSQL:
            from databases.mysql_database import MySQLDatabase
            return MySQLDatabase(name)
        elif db_type == DatabaseType.POSTGRE_SQL:
            from databases.postgresql_database import PostgreSQLDatabase
            return PostgreSQLDatabase(name)
        elif db_type == DatabaseType.MONGO_DB:
            from databases.mongodb_database import MongoDBDatabase
            return MongoDBDatabase(name)
        else:
            raise ValueError(f"Unknown database type: {db_type}")
