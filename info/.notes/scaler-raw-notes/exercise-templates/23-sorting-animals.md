# Sorting using Streams - Sort Animals

Source folder: 1773391601_209b717e803e749b/Sorting_using_St-solution

## Problem Statement

You are given a list of strings which stores the names of animals. Your task is to use streams and lambdas to sort the given list according to the length of the strings in descending order of length.

If two or more strings have the same size then return in the order in which they exist in the original list (stable sort).

## Graded Contract (from tests)

- **Class**: `AnimalSorter` (package `org.example`)
- **Method**: `public static List<String> sortAnimalsByLengthDescending(List<String> animals)`
  - Input: List of String objects
  - Output: List<String> sorted by length descending (stable for equal lengths)
  - Called directly in test with 3 test cases (mixed lengths, all same length, empty list)
  - Comparison uses equals() on result list

## Learner Template

```java
package org.example;

import java.util.List;

public class AnimalSorter {
    public static List<String> sortAnimalsByLengthDescending(List<String> animals) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Import statements for streams, Collectors
- Stream chain logic: sorted(Comparator), collect(Collectors.toList())
- The exact comparator logic: Integer.compare() with reversed order
- main() method with example usage and test data
