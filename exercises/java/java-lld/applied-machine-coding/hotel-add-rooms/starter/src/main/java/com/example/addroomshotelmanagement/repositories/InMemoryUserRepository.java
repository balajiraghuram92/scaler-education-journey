package com.example.addroomshotelmanagement.repositories;

import com.example.addroomshotelmanagement.models.User;

import java.util.*;

// TODO: implement UserRepository as an in-memory store keyed by user id — findById(...)
// returns an Optional wrapping the stored user (empty if absent, don't use Optional.of
// on a possibly-null value); save(...) assigns an id when the user doesn't already have
// one (id == 0) and stores it in the map.
public class InMemoryUserRepository implements UserRepository {
    private Map<Long, User> userMap;
    private static long id = 0;

    public InMemoryUserRepository() {
        userMap = new HashMap<>();
    }

    @Override
    public Optional<User> findById(long userId) {
        return null;
    }

    @Override
    public User save(User user) {
        return null;
    }
}
