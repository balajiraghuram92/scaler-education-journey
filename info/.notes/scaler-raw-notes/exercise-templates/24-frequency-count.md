# Frequency Count

Source folder: 1773391633_35188efa5a99b024/Frequency_Count-solution

## Problem Statement

You are given an array of integers, and you need to count the frequency of each integer present in the array using a `Map` and return the map as the answer.

- Use `Map<Integer,Integer>` to solve the question.
- The keys of the map are the elements of the array.
- The values of the map are the frequencies of those elements.

## Graded Contract (from tests)

- **Class**: `FrequencyCounter` (package `org.example`)
- **Method**: `public static Map<Integer, Integer> countFrequencies(int[] nums)`
  - Input: int[] array
  - Output: Map<Integer, Integer> where keys are elements and values are frequencies
  - Called directly in test with 3 test cases (mixed frequencies, all same value, all unique values, empty array)
  - Comparison uses equals() on result map

## Learner Template

```java
package org.example;

import java.util.Map;

public class FrequencyCounter {
    public static Map<Integer, Integer> countFrequencies(int[] nums) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Import statements for HashMap
- HashMap instantiation and initialization logic
- Iteration over array elements
- getOrDefault() logic for incrementing counts
- main() method with example usage and test data
