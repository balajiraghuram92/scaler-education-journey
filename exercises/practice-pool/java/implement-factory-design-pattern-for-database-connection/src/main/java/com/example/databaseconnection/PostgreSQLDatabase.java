package com.example.databaseconnection;

public class PostgreSQLDatabase extends Database {

    public PostgreSQLDatabase(String databaseName) {
        super(databaseName);
    }

    @Override
    public void databaseConnection() {
        //Implement the logic to connect Postgre Database
        System.out.println("Connecting to Postgre Database");
    }

    @Override
    public DatabaseType supportsType() {
        return DatabaseType.POSTGRE_SQL;
    }
}
