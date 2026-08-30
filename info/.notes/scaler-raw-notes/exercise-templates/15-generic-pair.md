# Generic Pair Class Implementation

Source folder: `1773391566_f1fbbdf18e73d41b/Generic_Pair-solution`

## Problem Statement

Design and implement a generic class named Pair that encapsulates a pair of values, where these values can be of any type. The class should provide mechanisms to store two values of generic types and methods to access these values. Ensure your implementation is generic enough to support pairs of different types.

### Instructions

1. Declare two private instance variables within the `Pair` class to store the pair values. The types of these variables should be generic, allowing for any object type.
2. Implement a constructor for the `Pair` class that initializes the pair with two values. The constructor should accept two parameters corresponding to the types of the pair values.
3. Implement methods `getFirst()` and `getSecond()` within the `Pair` class to retrieve the first and second values of the pair, respectively.

## Graded Contract (from tests)

From `TestPair.java`:

- Class `Pair<T, U>` must exist with two type parameters
- Must have constructor `Pair(T first, U second)` that accepts two parameters of potentially different types
- Must have method `T getFirst()` returning the first value
- Must have method `U getSecond()` returning the second value
- Constructor must accept null values
- Must work with mixed types (e.g., Integer and String, String and Double, Boolean and Boolean)
- Must preserve boundary values (Integer.MIN_VALUE, Integer.MAX_VALUE)

## Learner Template

```java
package org.example;

public class Pair<T, U> {

    // Private instance variables for storing pair values
    // TODO: Declare private T first and private U second

    public Pair(T first, U second) {
        // TODO: Initialize first and second
    }

    public T getFirst() {
        // TODO: Return first value
    }

    public U getSecond() {
        // TODO: Return second value
    }
}
```

## Deliberately Left Out (for the learner to design)

- Main method with example usage and demonstrations
- Choice of how to initialize fields in constructor
- Any additional utility methods not required by the contract
