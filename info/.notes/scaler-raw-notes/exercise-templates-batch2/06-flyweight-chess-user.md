# Flyweight Pattern for Chess User Optimization

Source folder: `1773391256_7c2c28d4699350ff/Flyweight_Docume-solution`

## Problem Statement

You are developing a chess game application where you need to represent individual chess users with various attributes like name, age, gender, email, and more. One user can play multiple games simultaneously. At the moment, you create a new user object for each game. Each user object consumes memory, and you want to optimize the memory usage by only keeping one copy of fields that do not change.

You need to implement the Flyweight pattern to efficiently manage and reuse shared attributes while keeping individual user-specific data separate.

## Detailed Requirements

### Task 1 - Intrinsic and Extrinsic State Separation

In the Flyweight pattern, objects are divided into intrinsic state (shared and independent of the context) and extrinsic state (variable and dependent on the context). Your task is to refactor the `ChessUser` class into two separate classes: `ChessUserIntrinsicState` and `ChessUserExtrinsicState`.

**ChessUserIntrinsicState class:**
- Create a class named `ChessUserIntrinsicState` with appropriate fields to represent the intrinsic state of a chess user.
- Annotate this class with the `@IntrinsicState` annotation to mark it as the intrinsic state container.

**ChessUserExtrinsicState class:**
- Create a class named `ChessUserExtrinsicState` with appropriate fields to represent the extrinsic state of a chess user.
- Annotate this class with the `@ExtrinsicState` annotation to indicate it contains the extrinsic state.

### Task 2 - Implementing the Flyweight Registry

To make the storage and retrieval of flyweight objects easier, implement a registry pattern.

- Create a registry class that implements the `FlyweightRegistry` interface.
- This class should manage the flyweight objects and provide methods to add and retrieve flyweights based on their type.

### Instructions

1. Implement the `ChessUserIntrinsicState` and `ChessUserExtrinsicState` classes by separating the original `ChessUser` class into intrinsic and extrinsic state.
2. Ensure that both classes are annotated with the appropriate annotations, i.e., `@IntrinsicState` and `@ExtrinsicState`.
3. Implement the registry class according to the `FlyweightRegistry` interface. This class should store and provide access to flyweight objects based on their type.
4. Run the provided test cases in the `ChessUserTest` class to validate the correctness of your Flyweight pattern implementation.

## Any Given "Before" Code

Original `ChessUser` class:
```java
public class ChessUser {
    private String name;
    private int age;
    private String gender;
    private String email;
    private String phoneNumber;
    private Colour colour;
    private int currentGameStreak;
    private Byte[] photo;
}
```

Intrinsic fields (same across games): name, age, gender, email, phoneNumber, photo
Extrinsic fields (vary per game): colour, currentGameStreak

## Graded Contract (from tests)

- **@IntrinsicState annotation:** Exactly one class must be annotated with `@IntrinsicState`
- **UserIntrinsicState fields:** Must contain fields: `name`, `age`, `gender`, `email`, `phoneNumber`, `photo`
- **@ExtrinsicState annotation:** Exactly one class must be annotated with `@ExtrinsicState`
- **UserExtrinsicState fields:** Must contain fields: `colour`, `currentGameStreak`
- **ExtrinsicState reference field:** UserExtrinsicState must have a field of type UserIntrinsicState
- **FlyweightRegistry implementation:** Must be a concrete class implementing `FlyweightRegistry` interface
- **Registry storage:** FlyweightRegistry implementation must have a `Map` field for storing/fetching flyweights

## Learner Template

```java
// UserIntrinsicState.java
package com.assignment.question;

import lombok.Getter;

@IntrinsicState
@Getter
public class UserIntrinsicState {
    private String name;
    private int age;
    private String gender;
    private String email;
    private String phoneNumber;
    private Byte[] photo;
}
```

```java
// UserExtrinsicState.java
package com.assignment.question;

@ExtrinsicState
public class UserExtrinsicState {
    private Colour colour;
    private int currentGameStreak;
    private UserIntrinsicState user;
}
```

```java
// FlyweightRegistry interface (already provided)
package com.assignment.question;

public interface FlyweightRegistry {
    void addFlyweight(UserIntrinsicState flyweight);
    UserIntrinsicState getFlyweight(String email);
}
```

```java
// FlyweightRegistryImpl.java - Learner must implement this
package com.assignment.question;

import java.util.HashMap;
import java.util.Map;

public class FlyweightRegistryImpl implements FlyweightRegistry {
    private Map<String, UserIntrinsicState> registry = new HashMap<>();

    @Override
    public void addFlyweight(UserIntrinsicState flyweight) {
        // TODO: implement
    }

    @Override
    public UserIntrinsicState getFlyweight(String email) {
        // TODO: implement
    }
}
```

## Deliberately Left Out (for the learner to design)

- Implementation logic in `FlyweightRegistryImpl.addFlyweight()` and `getFlyweight()` methods
- Any getter/setter methods for UserExtrinsicState fields (learners may add as needed)
- Getters for UserIntrinsicState fields (already provided via Lombok `@Getter`)
