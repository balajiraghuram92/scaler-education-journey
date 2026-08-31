package com.example.databaseconnection;

public class MongoDBDatabase extends Database {
    public MongoDBDatabase(String databaseName) {
        super(databaseName);
    }

    @Override
    public void databaseConnection() {
        //Implement the logic to connect MongoDB Database
        System.out.println("Connecting to MongoDB Database");
    }

    @Override
    public DatabaseType supportsType() {
        return DatabaseType.MONGO_DB;
    }
}
