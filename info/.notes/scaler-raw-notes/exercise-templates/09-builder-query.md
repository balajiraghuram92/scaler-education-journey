# Builder Pattern Implementation for Building Queries

Source folder: `1773391241_6512dd2d3278e2d9/Builder_-_Query-solution`

## Problem Statement

You are tasked with developing a database management system that involves creating and executing SQL queries. Queries can vary in complexity, involving different SELECT clauses, JOIN operations, WHERE conditions, and more. The current approach of constructing queries using concatenated strings has proven to be error-prone, difficult to read, and challenging to modify. You should implement the Builder pattern to create instances of query objects with various configurations, resulting in more maintainable and flexible code.

Your task is to implement the Builder pattern to construct query objects with different configurations. The Builder pattern facilitates the step-by-step construction of complex objects while keeping the creation process separate from the main object.

## Graded Contract (from tests)

- **Class `Query`** (reference/original class)
  - Fields: `select` (String), `from` (String), `where` (String), `join` (String), `orderBy` (String), `groupBy` (String)
  - Constructor and getters for all fields

- **Annotation `@WithBuilder`**
  - Marks the builder implementation class
  - Must be exactly one class in the package annotated with this

- **Builder outer class** (annotated with `@WithBuilder`)
  - Must have all fields from Query with matching names and types
  - Must have a public no-args constructor
  - Static inner class `Builder` that is public and static

- **Static inner class `Builder`**
  - Constructor: `public Builder()` — no-args constructor
  - Must either:
    - Have fields matching all Query fields, OR
    - Have a field that references the outer builder class instance
  - Method: `build()` — returns instance of outer class with all field values copied
  - Builder methods (select, from, where, join, orderBy, groupBy) for fluent API

- **Test contract details**
  - Tests use reflection to find `@WithBuilder` annotated class
  - Tests check that all fields from Query exist in the builder
  - Tests verify Builder inner class copies values correctly

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
public class QueryBuilder {
    private String select;
    private String from;
    private String where;
    private String join;
    private String orderBy;
    private String groupBy;

    public QueryBuilder() {
        // TODO: implement
    }

    public static Builder builder() {
        // TODO: implement - return new Builder instance
    }

    public static class Builder {
        private QueryBuilder queryBuilder;

        public Builder() {
            // TODO: implement
        }

        public Builder select(String select) {
            // TODO: implement
        }

        public Builder from(String from) {
            // TODO: implement
        }

        public Builder where(String where) {
            // TODO: implement
        }

        public Builder join(String join) {
            // TODO: implement
        }

        public Builder orderBy(String orderBy) {
            // TODO: implement
        }

        public Builder groupBy(String groupBy) {
            // TODO: implement
        }

        public QueryBuilder build() {
            // TODO: implement - create new outer instance with field values
        }
    }
}
```

## Deliberately Left Out (for the learner to design)

- Private field initialization and persistence logic in QueryBuilder
- Builder method implementations (chaining logic via returning `this`)
- Build method instantiation and field copying logic
- Whether to use an internal reference to QueryBuilder in Builder or duplicate fields
- Getter methods (not required by contract)
- SQL concatenation logic (if any)
