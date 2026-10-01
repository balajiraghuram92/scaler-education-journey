package com.example.bmsbookticket.repositories;

import com.example.bmsbookticket.models.User;

import java.util.List;
import java.util.Optional;

public interface UserRepository {
    User save(User user);

    Optional<User> findById(int id);

    List<User> findAll();
}
