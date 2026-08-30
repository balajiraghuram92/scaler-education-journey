# Count Unique Words

Source folder: 1773391586_8509bdcb01e23316/Count_Unique_Wor-solution

## Problem Statement

Given a list of strings representing sentences, write a Java method called `countWords` that performs the following operations using Java streams:

- Filter out sentences that don't contain the word `"Java"`.
- Map each filtered sentence to a list of unique words (remove duplicates).
- Flatten the list of unique words into a single stream of words using flatMap.
- Count the total number of remaining words.
- Return the count of remaining words.

## Graded Contract (from tests)

- **Class**: `WordCounter` (package `org.example`)
- **Method**: `public static long countWords(List<String> sentences)`
  - Input: List of String objects
  - Output: long (count of unique words in sentences without "Java"; 0 if no matches or empty list)
  - Called directly in test with 3 test cases (mix of Java and non-Java sentences, only non-Java sentences, empty list)

## Learner Template

```java
package org.example;

import java.util.List;

public class WordCounter {
    public static long countWords(List<String> sentences) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Import statements for streams, Arrays
- Stream chain logic: filter, map (split), flatMap, distinct, count
- The exact filter condition (!sentence.contains("Java"))
- String splitting regex pattern
- The flatMap(Arrays::stream) idiom for flattening arrays to stream
- main() method with example usage and test data
