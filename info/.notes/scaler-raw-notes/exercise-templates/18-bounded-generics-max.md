# Maximum Element Finder Using Bounded Generics

Source folder: `1773391576_ec5525e06fe1b4bb/Bounded_Generics-solution`

## Problem Statement

Develop a method named `findMax` that utilizes bounded generics to identify and return the maximum element from an array. The elements of the array must implement the `Comparable` interface, ensuring the method works with any type that has a natural ordering. The method should handle `null` or empty arrays gracefully, returning `null` in such cases.

### Instructions

1. Implement the `findMax` method within the `FindMaxElement` class. This method should be generic and use bounded generics to restrict its parameters to types that extend the `Comparable` interface.
2. The `findMax` method should accept an array of a generic type that extends `Comparable` and return the maximum element found in the array.
3. In the case of a `null` or empty array, the method should return null without throwing an exception.

## Graded Contract (from tests)

From `TestFindMaxElement.java`:

- Class `FindMaxElement` must exist in package `org.example`
- Must have static generic method: `<T extends Comparable<T>> T findMax(T[] array)`
- Must return the maximum element in the array using `compareTo()` method
- Must return `null` if array is `null`
- Must return `null` if array is empty
- Must work with Integer, Double, String, Character, and Float types
- `findMax(new Integer[]{4, 7, 1, 9, 3, 5})` should return `9`
- `findMax(new Double[]{3.14, 2.71, 1.618, 2.718})` should return `3.14`
- `findMax(new String[]{"Apple", "Banana", "Peach", "Orange"})` should return `"Peach"` (lexicographic order)
- `findMax(new Character[]{'a', 'e', 'i', 'o', 'u'})` should return `'u'`
- `findMax(new Integer[]{-1, -3, -7, -4})` should return `-1`
- `findMax(null)` should return `null`
- `findMax(new Integer[]{})` should return `null`

## Learner Template

```java
package org.example;

public class FindMaxElement {

    public static <T extends Comparable<T>> T findMax(T[] array) {
        // TODO: Handle null array - return null
        // TODO: Handle empty array - return null
        // TODO: Find maximum element using compareTo()
        // TODO: Return the maximum element found
    }
}
```

## Deliberately Left Out (for the learner to design)

- Main method with example usage and demonstrations
- Traversal and comparison logic details
- Any helper methods for finding max
- Specific exception handling (none needed - return null instead)
