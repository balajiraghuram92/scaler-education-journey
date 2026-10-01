package com.example.splitwise.repositories;

import com.example.splitwise.models.User;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

public class InMemoryUserRepository implements UserRepository {
    private final Map<Long, User> users = new ConcurrentHashMap<>();
    private final AtomicLong idCounter = new AtomicLong(0);

    @Override
    public User save(User user) {
        if (user.getId() == 0) {
            user.setId(idCounter.incrementAndGet());
        }
        users.put(user.getId(), user);
        return user;
    }

    @Override
    public Optional<User> findById(long userId) {
        return Optional.ofNullable(users.get(userId));
    }
}
