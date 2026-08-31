package com.example.databaseconnection;

// TODO: implement Database — supportsType() returns DatabaseType.MYSQL,
// databaseConnection() prints something describing the connection (any implementation
// is fine, it isn't asserted on).
public class MySQLDatabase extends Database {
    public MySQLDatabase(String databaseName) {
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
