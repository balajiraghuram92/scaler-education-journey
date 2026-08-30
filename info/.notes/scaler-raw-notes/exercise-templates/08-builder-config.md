# Builder Pattern Implementation for Database Configuration

Source folder: `1773391233_e5a95b2f17cb4988/Builder_Configur-solution`

## Problem Statement

You are tasked with creating a system-wide database configuration for a complex software suite. The configuration is responsible for managing various configuration settings that affect the data layer. To ensure a flexible and readable way to create configuration instances that are immutable, you decide to implement the Builder pattern.

Your task is to implement the Builder pattern to create instances of a configuration manager class. The Builder pattern allows for step-by-step construction of complex objects while keeping the creation process separate from the main object.

## Graded Contract (from tests)

- **Class `DatabaseConfiguration`** (reference/original class)
  - Fields: `databaseUrl` (String), `username` (String), `password` (String), `maxConnections` (int), `enableCache` (boolean), `isReadOnly` (boolean)
  - Constructor and getters for all fields

- **Annotation `@WithBuilder`**
  - Marks the builder implementation class
  - Must be exactly one class in the package annotated with this

- **Builder outer class** (annotated with `@WithBuilder`)
  - Must have all fields from DatabaseConfiguration with matching names and types
  - Must have a public no-args constructor
  - Static inner class `Builder` that is public and static

- **Static inner class `Builder`**
  - Constructor: `public Builder()` — no-args constructor
  - Must either:
    - Have fields matching all DatabaseConfiguration fields, OR
    - Have a field that references the outer builder class instance
  - Method: `build()` — returns instance of outer class with all field values copied

- **Test contract details**
  - Tests use reflection to find the `@WithBuilder` annotated class
  - Tests check that all fields from DatabaseConfiguration exist in the builder
  - Tests verify the Builder inner class copies values from builder to the built instance

## Learner Template

```java
package com.assignment.question;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
public @interface WithBuilder {
}
```

```java
package com.assignment.question;

@WithBuilder
public class DatabaseConfigurationBuilder {
    private String databaseUrl;
    private String username;
    private String password;
    private int maxConnections;
    private boolean enableCache;
    private boolean isReadOnly;

    public DatabaseConfigurationBuilder() {
        // TODO: implement
    }

    public static Builder builder() {
        // TODO: implement - return new Builder instance
    }

    public static class Builder {
        private DatabaseConfigurationBuilder databaseConfigurationBuilder;

        public Builder() {
            // TODO: implement
        }

        public Builder withDatabaseUrl(String databaseUrl) {
            // TODO: implement
        }

        public Builder withCredentials(String username, String password) {
            // TODO: implement
        }

        public Builder withMaxConnections(int maxConnections) {
            // TODO: implement
        }

        public Builder withEnableCache(boolean enableCache) {
            // TODO: implement
        }

        public Builder withReadOnly(boolean isReadOnly) {
            // TODO: implement
        }

        public DatabaseConfigurationBuilder build() {
            // TODO: implement - create new outer instance with field values
        }
    }
}
```

## Deliberately Left Out (for the learner to design)

- Private field initialization and persistence logic in DatabaseConfigurationBuilder
- Builder method implementations (chaining logic via returning `this`)
- Build method instantiation and field copying logic
- Whether to use an internal reference to DatabaseConfigurationBuilder in Builder or duplicate fields
- Getter methods (not required by contract)
