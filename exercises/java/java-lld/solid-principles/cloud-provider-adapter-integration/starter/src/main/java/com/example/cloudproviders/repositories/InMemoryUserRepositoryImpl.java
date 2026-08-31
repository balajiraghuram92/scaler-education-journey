package com.example.cloudproviders.repositories;

import com.example.cloudproviders.models.User;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

// TODO: implement UserRepository as an in-memory store keyed by user id — save(...)
// should assign an id when the user doesn't already have one (id == 0) and put the
// user into the map; findUserById(...) should return an Optional wrapping the stored
// user, or empty if no such id exists.
public class InMemoryUserRepositoryImpl implements UserRepository {
    private Map<Long, User> userMap;

    public InMemoryUserRepositoryImpl() {
        this.userMap = new HashMap<>();
    }

    @Override
    public User save(User user) {
        return null;
    }

    @Override
    public Optional<User> findUserById(long userId) {
        return null;
    }
}
