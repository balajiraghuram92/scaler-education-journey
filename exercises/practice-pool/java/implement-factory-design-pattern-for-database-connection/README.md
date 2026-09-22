# Implement Factory Design Pattern for Database Connection

## Problem Statement
You are building an application with which you need to connect a Database. Depending on the type of database (e.g., MySQL, Postgre SQL, Mongo DB), different type of database objects are required. You need a way to create database object without explicitly specifying their classes, ensuring the application is open for future database types.

Your task is to implement the Factory pattern to create Database objects. The Factory pattern provides a way to create objects without exposing the instantiation logic, allowing for easy addition of new database types.

### Task 1 - Creating a Common Parent Class - Database
To streamline the creation of Databases, implement the common parent class named Database. This class should include attributes and methods that are common to all the databases. The method supportsType has already been abstracted out for you as an example. You will need to implement the Database class as a common parent class for all Database Types.

### Task 2 - Implementing the Factory Pattern
Implement the DatabaseFactory class that follows the Simple Factory pattern. This class should have a method to create Database object based on the DatabaseType. The factory class should be capable of creating different types of databases based on the DatabaseType. Also remember that to create a database, you need to pass the database name as a parameter as well.

### Instructions
* Implement the Database class as a common parent class for all type of Databases. Include attributes and methods that are common to all Databases.

* Implement the DatabaseFactory class that implements the Simple Factory pattern. Add a method to create database based on DatabaseType and other parameters.
