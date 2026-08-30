# Generic Array Printing Method

Source folder: `1773391570_78eb4a9450256789/Generic_Print_Fu-solution`

## Problem Statement

Develop a generic method named `printArray` within a class named `PrintArrayElements`. This method should be capable of printing the elements of any array, regardless of its data type, to the console. Each element should be followed by a space, and no newline character should be printed after the last element. The purpose of this assignment is to familiarize you with generics in Java, allowing you to work with arrays of different types using a single method.

### Instructions

1. Inside the `PrintArrayElements` class, implement the `printArray` method. This method should be generic, enabling it to accept an array of any type as its parameter.
2. The method should iterate through the array and print each element followed by a space. Ensure that no newline character is printed after the last element of the array.

## Graded Contract (from tests)

From `TestPrintArrayElements.java`:

- Class `PrintArrayElements` must exist in package `org.example`
- Must have static generic method: `<T> void printArray(T[] array)`
- Must print each element followed by a space
- Must NOT print newline after the last element
- Must handle empty arrays (print nothing)
- Must handle single-element arrays
- Must handle null elements in arrays (print "null")
- Must work with Integer, String, Double, Character arrays
- `printArray(new Integer[]{1, 2, 3, 4, 5})` should output `"1 2 3 4 5 "` (with trailing space)
- `printArray(new String[]{"apple", "banana", "orange"})` should output `"apple banana orange "`
- `printArray(new Integer[]{})` should output `""`
- `printArray(new Integer[]{42})` should output `"42 "`

## Learner Template

```java
package org.example;

public class PrintArrayElements {

    public static <T> void printArray(T[] array) {
        // TODO: Iterate through array and print each element followed by a space
        // TODO: Do not print newline at the end
    }
}
```

## Deliberately Left Out (for the learner to design)

- Main method with example usage
- Any helper methods or loop constructs (learner must design the iteration)
- Specific printing implementation details
