# Group Anagrams

Source folder: `1773391636_5e88e5a1d9b5336f/Group_Anagrams-solution`

## Problem Statement

You are given an array of strings, you need to group the anagrams together and store them in a list of strings. Write a function in Java that takes an array of strings as input and returns a `List<List<String>>` where each inner list contains the strings that are grouped together i.e. the anagrams.

**Note:** A string `s2` is called an anagram of string s1, if the frequency of each character in the string s2 is equal to the frequency of each character in the string `s1`.

### Example
Let us consider the array of strings given as input be ["eat", "tea", "tan"]. Now, if we look at the array we can see that "eat" and "tea" are anagrams because in "eat" the characters are 'e','a' & 't' having frequency of 1 each. Similarly, "tea" also has 'a','e' & 't' characters only and their frequency is also 1 each. Since all the characters have the same frequency and all the characters are common in both strings hence they are anagrams.

We group these anagrams together in a list which will look like ["eat","tea"]. Since "tan" has no anagram therefore the list for anagrams of "tan" has only one string (which is "tan" itself).

## Graded Contract (from tests)

- Class `AnagramGrouper` must exist in package `org.example`
- Static method `groupAnagrams(String[])` returning `List<List<String>>`
  - Must handle null input (return empty list)
  - Must handle empty array (return empty list)
  - Must group anagrams together based on character frequency
  - Must maintain input order (use LinkedHashMap as per hint)
  - Must return a list of lists where each inner list contains anagrams

## Learner Template

```java
package org.example;

import java.util.*;

public class AnagramGrouper {
    public static List<List<String>> groupAnagrams(String[] strs) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- The internal data structure (LinkedHashMap to maintain insertion order)
- Character sorting logic to identify anagrams
- Method to convert sorted characters back to string for use as map key
- The main method (optional helper)

## Notes

- Tests check for correct grouping of anagrams, handling of null/empty input, and maintaining input order
- No test file found for inheritance or interface checks
