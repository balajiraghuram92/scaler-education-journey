# Student Sorter

Source folder: `1773391643_d6ce16608f8d620f/Student_Sorter-solution`

## Problem Statement

You are given a class `Student` which stores the data of each student. The `Student` class has two variables, `name` and `age`. Now you are given a list of `Student` and you need to sort the given list of students according to their age in descending order, i.e. the student with the highest age comes first and the student with the lowest age comes last.

**Note:** You do not have to create a new list of students, just sort the given list according to age in descending order. If two or more Students have the same age then keep them in the same order as they appear in the input list.

## Graded Contract (from tests)

- Class `Student` must exist in package `org.example` with:
  - Constructor: `Student(String name, int age)`
  - Method: `String getName()`
  - Method: `int getAge()`
  - ToString method for display

- Class `StudentSorter` must exist in package `org.example` with:
  - Static method `sortStudentsByAgeDescending(List<Student>)` returning `void`
  - Must sort the list in-place in descending order by age
  - Must handle empty lists gracefully
  - Must handle single element lists
  - Must maintain relative order for students with same age (stable sort)

## Learner Template

```java
package org.example;

public class Student {
    public Student(String name, int age) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public String getName() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public int getAge() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

```java
package org.example;

import java.util.*;

public class StudentSorter {
    public static void sortStudentsByAgeDescending(List<Student> students) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Student class fields (name, age) and their initialization
- Comparator implementation using lambda or method reference
- List.sort() method usage with Comparator
- ToString method implementation
- Main method (optional helper)

## Notes

- Student class already provided in solution; learner should focus on StudentSorter
- Must use Comparator interface as per instructions
- Tests verify descending age order and stable sorting behavior for equal ages
- Edge cases tested: empty list, single element, already sorted, reverse sorted, mixed ages
