package com.example.splitwise.repositories;

import com.example.splitwise.models.Group;

import java.util.Optional;

public interface GroupRepository {
    Group save(Group group);

    Optional<Group> findById(long groupId);
}
