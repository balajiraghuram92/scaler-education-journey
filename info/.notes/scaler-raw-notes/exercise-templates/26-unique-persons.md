# Unique Persons

Source folder: `1773391639_57cd8804abf5e07e/Unique_Persons-solution`

## Problem Statement

You are given a class `Person` which stores the data of each person. The `Person` class has two variables, `name` and `age`. Now you are given a list of `Person` and you need to remove the duplicates from the given list and return the filtered list.

You need to remove the duplicates based on `name` only, irrespective of the age. If two or more persons have the same `name` but different ages, then include the person who came first in the list and discard others. The output must be in the same order as they occur in the input list.

## Graded Contract (from tests)

- Class `Person` must exist in package `org.example` with:
  - Constructor: `Person(String name, int age)`
  - Method: `String getName()`
  - Method: `int getAge()`
  - Equals method that compares based on name only
  - HashCode method consistent with equals

- Class `PersonManager` must exist in package `org.example` with:
  - Static method `removeDuplicatePersons(List<Person>)` returning `List<Person>`
  - Must handle null input (return empty list)
  - Must handle empty list (return empty list)
  - Must remove duplicates based on name only, keeping first occurrence
  - Must maintain input order

## Learner Template

```java
package org.example;

public class Person {
    public Person(String name, int age) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public String getName() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public int getAge() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

```java
package org.example;

import java.util.*;

public class PersonManager {
    public static List<Person> removeDuplicatePersons(List<Person> persons) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Person class fields (name, age) and their initialization
- HashSet logic for tracking seen names
- Logic to preserve insertion order while filtering
- Main method (optional helper)

## Notes

- Person class already provided in solution; learner should focus on PersonManager
- Tests verify order preservation and name-based deduplication
- Edge cases tested: null input, empty list, no duplicates, mixed duplicates
