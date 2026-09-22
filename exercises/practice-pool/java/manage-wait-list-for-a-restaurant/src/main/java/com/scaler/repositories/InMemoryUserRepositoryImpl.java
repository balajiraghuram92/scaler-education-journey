package com.scaler.repositories;

import com.scaler.models.User;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class InMemoryUserRepositoryImpl implements UserRepository{

    private Map<Long, User> users;

    public InMemoryUserRepositoryImpl() {
        this.users = new HashMap<>();
    }

    @Override
    public User save(User user) {
        if(user.getId() == 0){
            user.setId(users.size() + 1);
        }
        users.put(user.getId(), user);
        return user;
    }

    @Override
    public Optional<User> findById(long id) {
        return Optional.ofNullable(users.get(id));
    }
}
