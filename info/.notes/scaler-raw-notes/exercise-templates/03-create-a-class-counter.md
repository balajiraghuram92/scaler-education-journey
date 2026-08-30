# Create a Class Counter

Source folder: `1773391170_fd599c737388defa/Create_a_class_C-solution`

## Problem Statement

Lecture 7 Assignment 8 - Create a class Counter. This exercise covers synchronized methods and thread-safe access to shared mutable state.

## Graded Contract (from tests)

From `CounterTest.java`, the following must be present and function correctly:

- **Class `Counter`** (verified via `Class.forName("Counter")`)
  - Must have a `private int count` field (verified via reflection)
  - Must have a public constructor that accepts a single `int` parameter
    - Constructor must initialize the `count` field with the provided value
  - Must have a public synchronized `void incValue(int offset)` method
    - Signature: `void incValue(int)` with `public` and `synchronized` modifiers
    - Must add the offset to the count field
  - Must have a public synchronized `void decValue(int offset)` method
    - Signature: `void decValue(int)` with `public` and `synchronized` modifiers
    - Must subtract the offset from the count field
  - Must have a public synchronized `int getValue()` method
    - Signature: `int getValue()` with `public` and `synchronized` modifiers, returns int
    - Must return the current value of the count field

## Learner Template

```java
public class Counter {
    private int count;
    
    public Counter(int count) {
        // TODO: implement
    }
    
    public synchronized void incValue(int offset) {
        // TODO: implement
    }
    
    public synchronized void decValue(int offset) {
        // TODO: implement
    }
    
    public synchronized int getValue() {
        // TODO: implement
    }
}
```

## Deliberately Left Out (for the learner to design)

- Field initialization logic
- Arithmetic operations in incValue and decValue
- Return statement in getValue
- Any getter/setter methods beyond getValue
- Validation or error handling logic
- Helper methods or utility functions
