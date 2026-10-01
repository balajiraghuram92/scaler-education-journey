package com.example.splitwise.repositories;

import com.example.splitwise.models.User;

import java.util.Optional;

public interface UserRepository {
    User save(User user);

    Optional<User> findById(long userId);
}
