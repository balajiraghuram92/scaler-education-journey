package com.assignment.question;

import java.util.HashMap;
import java.util.Map;

// TODO: implement UserPrototypeRegistry — addPrototype(...) stores the given User
// keyed by its type; getPrototype(...) returns the stored prototype as-is; clone(...)
// looks up the stored prototype and returns cloneObject() on it.
public class UserPrototypeRegistryImpl implements UserPrototypeRegistry {
    private Map<UserType, User> users = new HashMap<>();
    @Override
    public void addPrototype(User user) {

    }

    @Override
    public User getPrototype(UserType type) {
        return null;
    }

    @Override
    public User clone(UserType type) {
        return null;
    }
}
