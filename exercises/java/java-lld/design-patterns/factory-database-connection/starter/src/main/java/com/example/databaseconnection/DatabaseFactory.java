package com.example.databaseconnection;

// TODO: implement the Simple Factory — createDatabase(...) should return a
// MySQLDatabase, PostgreSQLDatabase or MongoDBDatabase matching databaseType,
// constructed with databaseName, or throw IllegalArgumentException for anything else.
public class DatabaseFactory {
    public static Database createDatabase(DatabaseType databaseType, String databaseName) {
        return null;
    }
}
