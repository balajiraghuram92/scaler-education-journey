# Prototype Pattern for Object Cloning in Testing

Source folder: `1773391202_bb97330eb874cb37/Prototype_User-solution`

## Problem Statement

You are developing a testing framework for a user API of a social media platform. Each test case requires generating multiple mock users with different attributes to simulate various scenarios. However, creating mock users for testing involves complex setups and is time-consuming. To optimize the user creation process during testing, you decide to implement the Prototype pattern. This pattern allows you to create prototype objects and clone them when needed, avoiding the overhead of setting up complex user objects repeatedly.

Your task is to implement the Prototype pattern to create prototype objects for mock users in the testing framework. You should define a `ClonableObject` interface that contains the `cloneObject` method, which should be implemented by user objects. Additionally, you need to create a `UserPrototypeRegistry` interface that provides methods for adding and retrieving user prototypes and for cloning user objects. The goal is to streamline the process of creating mock users for testing.

## Graded Contract (from tests)

- **Interface `ClonableObject<T>`** with generic type parameter
  - Method: `T cloneObject()` — returns a cloned copy of type T

- **Class `User`** must implement `ClonableObject<User>`
  - Constructor: `User(long userId, String username, String email, String displayName, int age, UserType type)`
  - Getters: `getUserId()`, `getUsername()`, `getEmail()`, `getDisplayName()`, `getAge()`, `getType()`
  - Must override `cloneObject()` to return a new User instance with the same field values

- **Enum `UserType`** with at least these values:
  - `ADMIN`, `READER`, `WRITER`

- **Interface `UserPrototypeRegistry`**
  - Method: `void addPrototype(User user)` — adds a user prototype keyed by its type
  - Method: `User getPrototype(UserType type)` — retrieves the exact prototype object (not a clone)
  - Method: `User clone(UserType type)` — returns a cloned copy of the prototype for the given type

- **Implementation of `UserPrototypeRegistry`** (must be the only one in package)
  - Must have a public no-args constructor (detected via reflection)
  - Tests instantiate it with `getDeclaredConstructor().newInstance()`

## Learner Template

```java
package com.assignment.question;

public interface ClonableObject<T> {
    T cloneObject();
}
```

```java
package com.assignment.question;

public enum UserType {
    ADMIN,
    READER,
    WRITER
}
```

```java
package com.assignment.question;

public class User implements ClonableObject<User> {
    private long userId;
    private String username;
    private String email;
    private String displayName;
    private int age;
    private UserType type;

    public User(long userId, String username, String email, String displayName, int age, UserType type) {
        // TODO: implement
    }

    public long getUserId() {
        // TODO: implement
    }

    public String getUsername() {
        // TODO: implement
    }

    public String getEmail() {
        // TODO: implement
    }

    public String getDisplayName() {
        // TODO: implement
    }

    public int getAge() {
        // TODO: implement
    }

    public UserType getType() {
        // TODO: implement
    }

    @Override
    public User cloneObject() {
        // TODO: implement - must return new User with same field values
    }
}
```

```java
package com.assignment.question;

public interface UserPrototypeRegistry {
    void addPrototype(User user);

    User getPrototype(UserType type);

    User clone(UserType type);
}
```

```java
package com.assignment.question;

public class UserPrototypeRegistryImpl implements UserPrototypeRegistry {
    public UserPrototypeRegistryImpl() {
        // TODO: implement
    }

    @Override
    public void addPrototype(User user) {
        // TODO: implement
    }

    @Override
    public User getPrototype(UserType type) {
        // TODO: implement
    }

    @Override
    public User clone(UserType type) {
        // TODO: implement
    }
}
```

## Deliberately Left Out (for the learner to design)

- Private field declarations in User class (userId, username, email, displayName, age, type)
- Internal data structure in UserPrototypeRegistryImpl (e.g., HashMap to store prototypes by type)
- Constructor initialization logic for User and registry
- Getter implementations
- Clone method implementation details (creating new User instance)
- Registry add/get/clone logic (HashMap management)
