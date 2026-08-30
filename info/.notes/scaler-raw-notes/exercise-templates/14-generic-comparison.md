# Generic Comparison

Source folder: `1773391565_0af5b676bbd19df8/Generic_Comparis-solution`

## Problem Statement

Implement a generic method named `compare` that can compare two objects of any type that supports comparison (i.e., any type that implements the `Comparable` interface). This method should leverage the objects' `compareTo` method to perform the comparison.

### Instructions

1. Create a generic method `compare` within a class named `GenericComparison`.
2. The method should take two parameters of the same type and return the result of comparing the two.
3. Ensure the objects passed as parameters implement the `Comparable` interface.

## Graded Contract (from tests)

From `TestGenericComparison.java`:

- Class `GenericComparison` must exist in package `org.example`
- Must have static generic method: `<T extends Comparable<T>> int compare(T obj1, T obj2)`
- Method must return the result of calling `obj1.compareTo(obj2)`
- Must work with Integer, String, Double, and Character types
- `compare(5, 10)` should return `-1`
- `compare(-33, -33)` should return `0`
- `compare("apple", "banana")` should return `-1`
- `compare("mango", "banana")` should return `11`
- `compare('a', 'b')` should return `-1`

## Learner Template

```java
package org.example;

public class GenericComparison {

    public static <T extends Comparable<T>> int compare(T obj1, T obj2) {
        // TODO: Implement comparison logic
    }
}
```

## Deliberately Left Out (for the learner to design)

- Main method with example usage
- Test harness and demonstration code
