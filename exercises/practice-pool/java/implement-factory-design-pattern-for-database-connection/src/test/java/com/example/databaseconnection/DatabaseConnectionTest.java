package com.example.databaseconnection;

import org.junit.jupiter.api.Test;
import org.reflections.Reflections;
import org.reflections.scanners.SubTypesScanner;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Arrays;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class DatabaseConnectionTest {

    @Test
    public void testDatabaseClass() {
        String packageName = DatabaseConnectionTest.class.getPackageName();

        Reflections reflections = new Reflections(packageName, new SubTypesScanner(false));
        Set<Class<? extends Database>> subTypes = reflections.getSubTypesOf(Database.class);

        assertEquals(3, subTypes.size(),
                "There should be 3 implementations of Database class");

        boolean hasDatabaseName = Arrays.stream(Database.class.getDeclaredFields())
                .anyMatch(field -> field.getType().equals(String.class));

        assertTrue(hasDatabaseName, "Database class should have a String field `databaseName`");

        boolean hasSupportsType = Arrays.stream(Database.class.getDeclaredMethods())
                .anyMatch(method -> method.getName().equals("supportsType")
                        && method.getParameterCount() == 0
                        && method.getReturnType().equals(DatabaseType.class)
                        && Modifier.isAbstract(method.getModifiers()));
        assertTrue(hasSupportsType,
                "Database class should have a method called supportsType with no parameters and DatabaseType return type.");

        boolean hasDatabaseConnection = Arrays.stream(Database.class.getDeclaredMethods())
                .anyMatch(method -> method.getName().equals("databaseConnection")
                        && method.getParameterCount() == 0
                        && method.getReturnType().equals(void.class)
                        && Modifier.isAbstract(method.getModifiers()));
        assertTrue(hasDatabaseConnection,
                "Database class should have a method called databaseConnection with no parameters and void return type.");
    }

    @Test
    public void testDatabaseFactory() {
        boolean hasCreateDatabaseMethod = Arrays.stream(DatabaseFactory.class.getDeclaredMethods())
                .anyMatch(method -> Modifier.isStatic(method.getModifiers())
                        && method.getReturnType().equals(Database.class)
                        && Arrays.asList(method.getParameterTypes()).contains(DatabaseType.class)
                        && Arrays.asList(method.getParameterTypes()).contains(String.class));

        assertTrue(hasCreateDatabaseMethod,
                "If the factory is implemented correctly, it should have a static method to create database that takes two parameters: DatabaseType and String databaseName.");
    }

    @Test
    public void testDatabaseFactoryMethodInvocation() {
        Method[] methods = DatabaseFactory.class.getDeclaredMethods();

        Method createDatabaseMethod = Arrays.stream(methods)
                .filter(method -> Modifier.isStatic(method.getModifiers())
                        && method.getReturnType().equals(Database.class)
                        && Arrays.asList(method.getParameterTypes()).contains(DatabaseType.class)
                        && Arrays.asList(method.getParameterTypes()).contains(String.class))
                .findFirst()
                .orElse(null);

        assertNotNull(createDatabaseMethod, "If the factory is implemented correctly, it should have a static method to " +
                "create database that takes two parameters: DatabaseType and String databaseName.");

        DatabaseType databaseType = DatabaseType.MYSQL;
        String databaseName = "productServiceDB";
        Database database = null;

        try {
            database = (Database) createDatabaseMethod.invoke(null, databaseType, databaseName);
        } catch (IllegalArgumentException | IllegalAccessException | InvocationTargetException e) {
            throw new RuntimeException(e);
        }

        if (database == null) {
            try {
                database = (Database) createDatabaseMethod.invoke(null, databaseName, databaseType);
            } catch (IllegalArgumentException | IllegalAccessException | InvocationTargetException e) {
                throw new RuntimeException(e);
            }
        }

        assertNotNull(database, "If the factory is implemented correctly, the createDatabase method should return a non-null Database.");
        assertEquals(DatabaseType.MYSQL, database.supportsType(), "If the factory is implemented correctly, the create method should return a MySQLDatabase for DatabaseType.MYSQL");
    }
}
