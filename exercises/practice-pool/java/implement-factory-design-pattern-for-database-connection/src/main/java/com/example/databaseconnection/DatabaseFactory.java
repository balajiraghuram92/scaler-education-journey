package com.example.databaseconnection;

public class DatabaseFactory {
    public static Database createDatabase(DatabaseType databaseType, String databaseName) {
        return switch (databaseType) {
            case MYSQL -> new MySQLDatabase(databaseName);
            case POSTGRE_SQL -> new PostgreSQLDatabase(databaseName);
            case MONGO_DB -> new MongoDBDatabase(databaseName);
            default -> throw new IllegalArgumentException("Database type not supported : " + databaseType);
        };
    }
}
