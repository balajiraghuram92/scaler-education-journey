# Scaler Learning Platform

Source folder: `1773391657_02f29031bea0964e/Scaler_Learning_-solution`

## Problem Statement

You are tasked with implementing a basic user management system for a learning platform called "Scaler". The system should allow the creation of users, both students and employees, and provide methods to display their information.

### Objectives

1. **Implement a User Class:** Create a `User` class encapsulating common attributes and behaviors for all users. This class should include:
   - `username`: A string representing the user's username.
   - `email`: A string representing the user's email address.
   - A constructor to initialize the `username` and `email` properties.
   - A `displayInfo()` method to print out the user's information.
   - Getter methods for each property.

2. **Implement a Student Subclass:** Develop a `Student` class that extends the `User` class, adding specific properties and functionalities for student users. This class should include:
   - `studentId`: An integer representing the unique identifier of the student.
   - `course`: A string representing the course in which the student is enrolled.
   - A constructor to initialize both inherited and new properties.
   - Overridden `displayInfo()` method that calls `super.displayInfo()`.
   - Getter methods for the new properties.

3. **Implement an Employee Subclass:** Create an `Employee` class that also extends the `User` class, tailored for employee users. This class should include:
   - `employeeId`: An integer representing the unique identifier of the employee.
   - `department`: A string representing the department in which the employee works.
   - A constructor to initialize both inherited and new properties.
   - Overridden `displayInfo()` method that calls `super.displayInfo()`.
   - Getter methods for the new properties.

## Graded Contract (from tests)

- Class `User` must exist in package `org.example` with:
  - Constructor: `User(String username, String email)`
  - Method: `String getUsername()`
  - Method: `String getEmail()`
  - Method: `void displayInfo()` that prints "Username: " and "Email: " with line separators

- Class `Student` must exist in package `org.example` extending `User` with:
  - Constructor: `Student(String username, String email, int studentId, String course)`
  - Method: `int getStudentId()`
  - Method: `String getCourse()`
  - Overridden method: `void displayInfo()` that calls super and prints "Student ID: " and "Course: "

- Class `Employee` must exist in package `org.example` extending `User` with:
  - Constructor: `Employee(String username, String email, int employeeId, String department)`
  - Method: `int getEmployeeId()`
  - Method: `String getDepartment()`
  - Overridden method: `void displayInfo()` that calls super and prints "Employee ID: " and "Department: "

- All output uses System.lineSeparator() for line breaks (platform-independent)

## Learner Template

```java
package org.example;

public class User {
    public User(String username, String email) {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public String getUsername() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public String getEmail() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public void displayInfo() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }
}
```

```java
package org.example;

public class Student extends User {
    public Student(String username, String email, int studentId, String course) {
        // TODO: implement - call super constructor and initialize fields
        throw new UnsupportedOperationException("TODO");
    }

    public int getStudentId() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public String getCourse() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public void displayInfo() {
        // TODO: implement - call super.displayInfo() and add student info
        throw new UnsupportedOperationException("TODO");
    }
}
```

```java
package org.example;

public class Employee extends User {
    public Employee(String username, String email, int employeeId, String department) {
        // TODO: implement - call super constructor and initialize fields
        throw new UnsupportedOperationException("TODO");
    }

    public int getEmployeeId() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    public String getDepartment() {
        // TODO: implement
        throw new UnsupportedOperationException("TODO");
    }

    @Override
    public void displayInfo() {
        // TODO: implement - call super.displayInfo() and add employee info
        throw new UnsupportedOperationException("TODO");
    }
}
```

## Deliberately Left Out (for the learner to design)

- Instance variable declarations and initialization in all three classes
- Main methods (optional helpers)
- Exact println statements and line separator handling in displayInfo methods
- Inheritance implementation details

## Notes

- This is a classic inheritance and polymorphism exercise
- Tests verify getter functionality with various input values including null
- DisplayInfo output must be verified character-for-character including line separators
- Tests check special characters in usernames (e.g., "john_doe@2024")
- Must use System.lineSeparator() to be platform-independent (not hardcoded \n)
