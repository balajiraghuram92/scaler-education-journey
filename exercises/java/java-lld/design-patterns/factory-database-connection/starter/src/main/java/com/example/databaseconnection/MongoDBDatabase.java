package com.example.databaseconnection;

// TODO: implement Database — supportsType() returns DatabaseType.MONGO_DB,
// databaseConnection() prints something describing the connection (any implementation
// is fine, it isn't asserted on).
public class MongoDBDatabase extends Database {
    public MongoDBDatabase(String databaseName) {
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
