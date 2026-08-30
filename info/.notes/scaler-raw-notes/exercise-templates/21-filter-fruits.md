# Filter Fruits

Source folder: 1773391589_ab9cf9aca0388fb0/Filter_Fruits-solution

## Problem Statement

You are given a list of strings having different fruit names. You need to filter out the names of fruits whose name starts from the character `A`.

Use streams to execute the operations and return a List of String containing the fruit names whose name starts with `A`.

## Graded Contract (from tests)

- **Class**: `FruitFilter` (package `org.example`)
- **Method**: `public static List<String> filterFruitsStartingWithA(List<String> fruits)`
  - Input: List of String objects
  - Output: List<String> containing fruits starting with 'A' in original order
  - Called directly in test with 4 test cases (fruits with A matches, all A fruits, no A fruits, empty list)
  - Comparison uses equals() on result list

## Learner Template

```java
package org.example;

import java.util.List;

public class FruitFilter {
    public static List<String> filterFruitsStartingWithA(List<String> fruits) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Import statements for streams, Collectors
- Stream chain logic: filter, collect(Collectors.toList())
- The exact filter condition (startsWith("A"))
- main() method with example usage and test data
