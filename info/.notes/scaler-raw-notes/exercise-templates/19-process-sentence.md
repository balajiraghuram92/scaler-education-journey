# Process Sentences

Source folder: 1773391583_b631dc50feb15153/Process_Sentence-solution

## Problem Statement

Given a list of strings representing sentences, write a Java method called `processSentences` that performs the following operations using Java streams:

- Filter sentences that contain the word `"Java"`.
- Map each filtered sentence to its length.
- Find the average length of the sentences.
- Convert the average length to an integer by rounding down.
- Return the rounded average length.

## Graded Contract (from tests)

- **Class**: `SentenceProcessor` (package `org.example`)
- **Method**: `public static int processSentences(List<String> sentences)`
  - Input: List of String objects
  - Output: int (average length of sentences containing "Java", rounded down; 0 if no matches or empty list)
  - Called directly in test with 3 test cases (sentences with Java, sentences without Java, empty list)

## Learner Template

```java
package org.example;

import java.util.List;

public class SentenceProcessor {
    public static int processSentences(List<String> sentences) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Import statements for streams and OptionalDouble
- Stream chain logic: filter, mapToInt, average, orElse
- The exact filter condition (contains("Java"))
- Conversion from OptionalDouble to int via casting
- main() method with example usage and test data
