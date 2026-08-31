package com.example.databaseconnection;

public class DatabaseFactory {
    public static Database createDatabase(DatabaseType databaseType, String databaseName) {
        switch (databaseType) {
            case MYSQL:
                return new MySQLDatabase(databaseName);
            case POSTGRE_SQL:
                return new PostgreSQLDatabase(databaseName);
            case MONGO_DB:
                return new MongoDBDatabase(databaseName);
            default:
                throw new IllegalArgumentException("Database type not supported : " + databaseType);
        }
    }
}
