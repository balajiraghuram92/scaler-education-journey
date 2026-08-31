package com.example.databaseconnection;

// TODO: implement Database — supportsType() returns DatabaseType.POSTGRE_SQL,
// databaseConnection() prints something describing the connection (any implementation
// is fine, it isn't asserted on).
public class PostgreSQLDatabase extends Database {

    public PostgreSQLDatabase(String databaseName) {
        super(databaseName);
    }

    @Override
    public void databaseConnection() {

    }

    @Override
    public DatabaseType supportsType() {
        return null;
    }
}
