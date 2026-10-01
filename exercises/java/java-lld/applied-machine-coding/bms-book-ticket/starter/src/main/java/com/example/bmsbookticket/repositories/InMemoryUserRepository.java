package com.example.bmsbookticket.repositories;

import com.example.bmsbookticket.models.User;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentSkipListMap;
import java.util.concurrent.atomic.AtomicInteger;

public class InMemoryUserRepository implements UserRepository {
    // Sorted by id so findAll() returns rows in insertion order, like a table scan on an identity key.
    private final Map<Integer, User> rows = new ConcurrentSkipListMap<>();
    private final AtomicInteger idCounter = new AtomicInteger(0);

    @Override
    public User save(User user) {
        if (user.getId() == 0) {
            user.setId(idCounter.incrementAndGet());
        }
        rows.put(user.getId(), user);
        return user;
    }

    @Override
    public Optional<User> findById(int id) {
        return Optional.ofNullable(rows.get(id));
    }

    @Override
    public List<User> findAll() {
        return new ArrayList<>(rows.values());
    }
}
