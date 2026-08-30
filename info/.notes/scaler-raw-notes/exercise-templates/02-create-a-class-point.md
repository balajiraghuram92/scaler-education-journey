# Create a Class Point

Source folder: `1773391161_b48b6c8a6a966ad6/Create_a_class_P-solution`

## Problem Statement

Lecture 3 Assignment 1 - Create a class Point. This exercise covers basic class design with inheritance and method overriding.

## Graded Contract (from tests)

From `ThreedPointTest.java`, the following must be present and function correctly:

- **Class `Point`**
  - Must have a `protected int x` field
  - Must have a `protected int y` field
  - Must have a public `void display()` method (no parameters, void return type)
  - `display()` must print coordinates in format "[x, y]\n" (e.g., "[1, 2]\n")

- **Class `ThreedPoint`**
  - Must extend `Point` class (verified via `Point.class.isAssignableFrom(ThreedPoint.class)`)
  - Must have a private `int z` field (accessed via reflection in tests)
  - Must override `void display()` method (public, no parameters, void return type)
  - Overridden `display()` must print coordinates in format "[x, y, z]\n" (e.g., "[1, 2, 3]\n")

## Learner Template

```java
public class Point {
    protected int x;
    protected int y;
    
    public void display() {
        // TODO: implement
    }
}
```

```java
public class ThreedPoint extends Point {
    private int z;
    
    @Override
    public void display() {
        // TODO: implement
    }
}
```

## Deliberately Left Out (for the learner to design)

- Constructors for Point and ThreedPoint (tests use reflection with no-arg constructor)
- Getter/setter methods (not required by graded contract)
- Field initialization logic
- Console output formatting details
- Mutator methods or other utility methods
