# Implement Factory Design Pattern for Database Connection

Source folder: 1773391484_86d37a1e94ef71c7/Database_factory-solution

## Problem Statement

You are building an application with which you need to connect a Database. Depending on the type of database (e.g., MySQL, Postgre SQL, Mongo DB), different type of database objects are required. You need a way to create database object without explicitly specifying their classes, ensuring the application is open for future database types.

Your task is to implement the Factory pattern to create Database objects. The Factory pattern provides a way to create objects without exposing the instantiation logic, allowing for easy addition of new database types.

## Detailed Requirements

### Task 1 - Creating a Common Parent Class - Database

To streamline the creation of Databases, implement the common parent class named Database. This class should include attributes and methods that are common to all the databases. The method supportsType has already been abstracted out for you as an example. You will need to implement the Database class as a common parent class for all Database Types.

### Task 2 - Implementing the Factory Pattern

Implement the DatabaseFactory class that follows the Simple Factory pattern. This class should have a method to create Database object based on the DatabaseType. The factory class should be capable of creating different types of databases based on the DatabaseType. Also remember that to create a database, you need to pass the database name as a parameter as well.

### Instructions

- Implement the Database class as a common parent class for all type of Databases. Include attributes and methods that are common to all Databases.
- Implement the DatabaseFactory class that implements the Simple Factory pattern. Add a method to create database based on DatabaseType and other parameters.

## Graded Contract (from tests)

- **Database abstract class** must have:
  - String field `databaseName` (any access modifier)
  - Abstract method `supportsType()` returning DatabaseType with no parameters
  - Abstract method `databaseConnection()` returning void with no parameters
  - Public getter `getDatabaseName()` returning String (inferred but not explicitly tested)
- **DatabaseFactory class** must have:
  - Static method taking DatabaseType and String parameters and returning Database
  - Method name can be any name (tests use reflection to find it)
- **Exactly 3 implementations** of Database class in the package (MYSQL, POSTGRE_SQL, MONGO_DB)
- **DatabaseType enum** with at least: MYSQL, POSTGRE_SQL, MONGO_DB

## Learner Template

### Database (Abstract Parent Class)

```java
package com.example.databaseconnection;

public abstract class Database {
    private String databaseName;

    public Database(String databaseName) {
        this.databaseName = databaseName;
    }

    public String getDatabaseName() {
        // TODO: Implement getter
    }

    public abstract void databaseConnection();

    public abstract DatabaseType supportsType();
}
```

### DatabaseType (Enum)

```java
package com.example.databaseconnection;

public enum DatabaseType {
    MYSQL,
    POSTGRE_SQL,
    MONGO_DB
}
```

### DatabaseFactory (Simple Factory)

```java
package com.example.databaseconnection;

public class DatabaseFactory {
    public static Database createDatabase(DatabaseType databaseType, String databaseName) {
        // TODO: Implement factory method using switch/if-else to create appropriate database type
        // Should support: MYSQL, POSTGRE_SQL, MONGO_DB
        // Should throw IllegalArgumentException for unsupported database type
    }
}
```

### MySQLDatabase (Concrete Implementation)

```java
package com.example.databaseconnection;

public class MySQLDatabase extends Database {
    public MySQLDatabase(String databaseName) {
        super(databaseName);
    }

    @Override
    public void databaseConnection() {
        // TODO: Implement MySQL-specific connection logic
    }

    @Override
    public DatabaseType supportsType() {
        // TODO: Return DatabaseType.MYSQL
    }
}
```

### PostgreSQLDatabase (Concrete Implementation)

```java
package com.example.databaseconnection;

public class PostgreSQLDatabase extends Database {
    public PostgreSQLDatabase(String databaseName) {
        super(databaseName);
    }

    @Override
    public void databaseConnection() {
        // TODO: Implement PostgreSQL-specific connection logic
    }

    @Override
    public DatabaseType supportsType() {
        // TODO: Return DatabaseType.POSTGRE_SQL
    }
}
```

### MongoDBDatabase (Concrete Implementation)

```java
package com.example.databaseconnection;

public class MongoDBDatabase extends Database {
    public MongoDBDatabase(String databaseName) {
        super(databaseName);
    }

    @Override
    public void databaseConnection() {
        // TODO: Implement MongoDB-specific connection logic
    }

    @Override
    public DatabaseType supportsType() {
        // TODO: Return DatabaseType.MONGO_DB
    }
}
```

## Deliberately Left Out (for the learner to design)

- Specific database connection logic in each databaseConnection() method
- Additional attributes or methods specific to each database type (e.g., connection pooling, query execution)
- Error handling or exception logging in database connections
- Configuration management for database credentials and connection parameters
- Connection pooling or lifecycle management
