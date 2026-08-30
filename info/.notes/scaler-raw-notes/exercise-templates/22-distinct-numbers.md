# Distinct Numbers

Source folder: 1773391595_4fbb2e732be4d8ad/Distinct_Numbers-solution

## Problem Statement

You are given a list of integers, and you need to use streams and lambdas to return all the distinct numbers that are present in the given list.

## Graded Contract (from tests)

- **Class**: `DistinctNumbers` (package `org.example`)
- **Method**: `public static List<Integer> getDistinctNumbers(List<Integer> numbers)`
  - Input: List of Integer objects
  - Output: List<Integer> containing distinct values in original order
  - Called directly in test with 5 test cases (mixed duplicates, all same, all distinct, negatives/large numbers, empty list)
  - Comparison uses equals() on result list

## Learner Template

```java
package org.example;

import java.util.List;

public class DistinctNumbers {
    public static List<Integer> getDistinctNumbers(List<Integer> numbers) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Import statements for streams, Collectors
- Stream chain logic: distinct(), collect(Collectors.toList())
- main() method with example usage and test data
- TestHelper utility class (used only in testing, not part of learner code)
