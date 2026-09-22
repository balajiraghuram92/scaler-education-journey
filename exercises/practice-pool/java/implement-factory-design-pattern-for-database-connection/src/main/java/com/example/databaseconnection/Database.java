package com.example.databaseconnection;

public abstract class Database {
    private String databaseName;

    public Database(String databaseName) {
        this.databaseName = databaseName;
    }

    public String getDatabaseName() {
        return databaseName;
    }

    public abstract void databaseConnection();

    public abstract DatabaseType supportsType();
}
