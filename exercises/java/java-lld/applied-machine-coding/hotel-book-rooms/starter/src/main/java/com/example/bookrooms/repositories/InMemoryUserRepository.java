package com.example.bookrooms.repositories;

import com.example.bookrooms.models.User;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

// TODO: implement UserRepository as an in-memory store keyed by user id — findById(...)
// returns an Optional wrapping the stored user (empty if absent, don't use Optional.of
// on a possibly-null value); save(...) assigns an id when absent (id == 0) and stores it.
public class InMemoryUserRepository implements UserRepository {
    private Map<Long, User> userMap;
    private static long id = 0;

    public InMemoryUserRepository() {
        this.userMap = new HashMap<>();
    }

    @Override
    public Optional<User> findById(long id) {
        return null;
    }

    @Override
    public User save(User user) {
        return null;
    }
}
