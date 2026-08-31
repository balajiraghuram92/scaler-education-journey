package com.example.databaseconnection;

// TODO: add a private String field for the database's name, set it via the
// constructor, and expose it through getDatabaseName(). databaseConnection() and
// supportsType() stay abstract — each concrete database implements its own.
public abstract class Database {
    private String databaseName;

    public Database(String databaseName) {
        this.databaseName = databaseName;
    }

    public String getDatabaseName() {
        return null;
    }

    public abstract void databaseConnection();

    public abstract DatabaseType supportsType();
}
