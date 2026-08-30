# Connection Pool (Singleton Pattern)

Source folder: `1773391277_f7facac847678c9c/Singleton_Pool-solution`

## Problem Statement

You are tasked with designing a connection pool for a database management module of a complex software application. The connection pool is responsible for managing database connections efficiently to avoid unnecessary overhead and ensure optimal resource usage. To prevent multiple instances of the connection pool manager and ensure thread-safe access to connections, you need to implement the Singleton design pattern along with the connection pool management functionality.

Your task is to implement the `ConnectionPool` interface that follows the Singleton design pattern to manage a pool of database connections.

### Part 1: Implementing Singleton and Connection Pool

1. **Implement the Singleton design pattern**: Create a class that implements the `ConnectionPool` interface. Implement the Singleton design pattern within this class to ensure that only one instance of the connection pool manager can exist within the program.

2. **Implement the `getInstance(int maxConnections)` and `resetInstance()` methods**: Implement the `getInstance(int maxConnections)` method. This method should return the singleton instance of the connection pool manager class. Also, implement the `resetInstance()` method to reset the singleton instance to `null`.

### Part 2: Connection Pool Management

In connection pooling, the aim is to efficiently handle a group of database connections. This ensures optimal resource usage and effective sharing of connections across different parts of the software.

You have to implement the following methods:

- `void initializePool()`: This method is responsible for initializing the connection pool. It should create a fixed number of connections and add them to the pool. Store the connections in a data structure of your choice, but you will have to track which connections are available and which ones are currently in use.
- `DatabaseConnection getConnection()`: This method is responsible for providing a connection to the caller. It should return a connection from the pool of available connections. Once a connection is returned, it should be marked as "unavailable" so that other parts of the software don't use it.
- `void releaseConnection(DatabaseConnection connection)`: This method is responsible for releasing a connection back to the pool. It should mark the connection as "available" so that other parts of the software can use it.
- `int getAvailableConnectionsCount()`: Implement this method to count how many "available" connections remain in the pool.
- `int getTotalConnectionsCount()`: This method is about determining the total number of connections, whether they are currently in use or not.

## Graded Contract (from tests)

From `ConnectionPoolTest.java`:

- Implementation class must implement `ConnectionPool` interface
- Implementation class must have **private constructor(s)** only (no public constructor allowed)
- Implementation class must have static method `getInstance(int maxConnections)` returning `ConnectionPool`
- Implementation class must have static method `resetInstance()` returning void
- Singleton must return same instance on multiple calls to `getInstance()`
- All 5 interface methods must be implemented and functional:
  - `void initializePool()` 
  - `DatabaseConnection getConnection()`
  - `void releaseConnection(DatabaseConnection connection)`
  - `int getAvailableConnectionsCount()`
  - `int getTotalConnectionsCount()`
- `getAvailableConnectionsCount()` must decrease when `getConnection()` is called
- `getAvailableConnectionsCount()` must increase when `releaseConnection()` is called
- `getTotalConnectionsCount()` must equal the `maxConnections` parameter passed to `getInstance()`

## Learner Template

```java
package com.assignment.question;

public class ConnectionPoolImpl implements ConnectionPool {

    private static ConnectionPool instance = null;

    // Constructor must be private (not public)
    private ConnectionPoolImpl(int maxConnections) {
        // TODO: Initialize maxConnections and connection data structure
        // TODO: Call initializePool()
    }

    public static ConnectionPool getInstance(int maxConnections) {
        // TODO: Implement singleton pattern
        // TODO: Return existing instance or create new one
    }

    public static void resetInstance() {
        // TODO: Reset instance to null
    }

    @Override
    public void initializePool() {
        // TODO: Create fixed number of connections
        // TODO: Add them to the pool
    }

    @Override
    public DatabaseConnection getConnection() {
        // TODO: Return a connection from available pool
        // TODO: Handle interrupts appropriately
    }

    @Override
    public void releaseConnection(DatabaseConnection connection) {
        // TODO: Return connection back to available pool
        // TODO: Handle null connections gracefully
    }

    @Override
    public int getAvailableConnectionsCount() {
        // TODO: Count available connections
    }

    @Override
    public int getTotalConnectionsCount() {
        // TODO: Return total number of connections (max capacity)
    }
}
```

## Deliberately Left Out (for the learner to design)

- Private fields for storing `maxConnections` and the connection pool data structure
- Choice of data structure for storing connections (e.g., queue, set, etc.)
- Constructor implementation details
- Thread-safety implementation details in connection pool operations
- Helper method `createConnection()` and its logic
- Exception handling details (e.g., handling `InterruptedException`)
